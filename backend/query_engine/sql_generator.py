"""
SQL Generator Module.
Generates verified, schema-grounded SQL using either Gemini LLM prompts or semantic templates.
Supports SQLite, PostgreSQL, and MySQL dialects.
"""

from typing import Optional, Dict, Any
from django.conf import settings
from ai.gemini_client import gemini_client
from ai.prompts import SQL_GENERATION_PROMPT
from ai.parser import clean_sql, format_schema_for_llm

class SQLGenerator:
    def __init__(self):
        self.llm = gemini_client

    def generate(
        self,
        question: str,
        dialect: str = "sqlite",
        schema_dict: Optional[Dict[str, Any]] = None,
        resolved_specification: Optional[str] = None,
        resolved_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generates SQL using Gemini if available, otherwise runs semantic fallback generator."""
        schema_text = format_schema_for_llm(schema_dict) if schema_dict else "No schema provided."
        current_date = getattr(settings, "CURRENT_DATE", "2026-09-26")

        # 1. Try Gemini LLM if configured
        if self.llm.is_available:
            prompt = SQL_GENERATION_PROMPT.format(
                schema=schema_text,
                dialect=dialect,
                question=question,
                resolved_specification=resolved_specification or "None (direct query)",
                current_date=current_date
            )
            raw_sql = self.llm.generate_text(prompt, temperature=0.1)
            if raw_sql:
                return clean_sql(raw_sql)

        # 2. Semantic Fallback Generator
        return self._semantic_generate(question, dialect, schema_dict, resolved_specification, resolved_context)

    def _semantic_generate(
        self,
        question: str,
        dialect: str,
        schema_dict: Optional[Dict[str, Any]],
        resolved_specification: Optional[str],
        resolved_context: Optional[Dict[str, Any]]
    ) -> str:
        q_lower = question.lower()
        context = resolved_context or {}
        metric = context.get("metric", "")
        time_filter = context.get("time_filter", "")

        tables = schema_dict.get("tables", {}) if schema_dict else {}
        table_names = set(tables.keys())

        # Resolve candidate table names
        def find_table(candidates, default):
            for c in candidates:
                if c in table_names:
                    return c
            return default

        cust_tbl = find_table(["customers", "clients", "users", "accounts"], "customers")
        orders_tbl = find_table(["orders", "sales_transactions", "sales", "invoices"], "orders")
        products_tbl = find_table(["products", "items", "inventory"], "products")
        details_tbl = find_table(["order_items", "order_details", "sales_items"], "order_items")

        # Helper to find column from introspected schema
        def find_col(tbl_name, candidates, default):
            if tbl_name in tables:
                cols = tables[tbl_name].get("columns", {})
                for c in candidates:
                    if c in cols:
                        return c
            return default

        cust_id = find_col(cust_tbl, ["customer_id", "id", "user_id"], "customer_id")
        cust_name = find_col(cust_tbl, ["customer_name", "name", "full_name"], "customer_name")
        orders_cust_fk = find_col(orders_tbl, ["customer_id", "user_id", "client_id"], "customer_id")
        orders_total = find_col(orders_tbl, ["total_amount", "amount", "total", "price"], "total_amount")
        order_pk = find_col(orders_tbl, ["order_id", "id"], "order_id")

        prod_id = find_col(products_tbl, ["product_id", "id", "item_id"], "product_id")
        prod_name = find_col(products_tbl, ["product_name", "name", "title"], "product_name")
        prod_category = find_col(products_tbl, ["category", "type", "department"], "category")
        oi_prod_fk = find_col(details_tbl, ["product_id", "item_id"], "product_id")
        oi_qty = find_col(details_tbl, ["quantity", "qty", "count"], "quantity")
        oi_price = find_col(details_tbl, ["unit_price", "price", "amount"], "unit_price")

        # Best customers / Top customers
        if "best customer" in q_lower or "top customer" in q_lower or "valuable customer" in q_lower:
            time_clause = ""
            if time_filter == "30_days":
                if dialect == "sqlite":
                    time_clause = " WHERE o.order_date >= date('2026-09-26', '-30 days')"
                elif dialect == "postgresql":
                    time_clause = " WHERE o.order_date >= '2026-09-26'::date - INTERVAL '30 days'"
                else:
                    time_clause = " WHERE o.order_date >= DATE_SUB('2026-09-26', INTERVAL 30 DAY)"

            if metric == "order_count":
                return (
                    f"SELECT c.{cust_id}, c.{cust_name}, COUNT(o.{order_pk}) AS total_orders, SUM(o.{orders_total}) AS total_spend\n"
                    f"FROM {cust_tbl} c\n"
                    f"JOIN {orders_tbl} o ON c.{cust_id} = o.{orders_cust_fk}\n"
                    f"{time_clause}\n"
                    f"GROUP BY c.{cust_id}, c.{cust_name}\n"
                    f"ORDER BY total_orders DESC\n"
                    f"LIMIT 10;"
                )
            else:
                return (
                    f"SELECT c.{cust_id}, c.{cust_name}, SUM(o.{orders_total}) AS total_spent, COUNT(o.{order_pk}) AS order_count\n"
                    f"FROM {cust_tbl} c\n"
                    f"JOIN {orders_tbl} o ON c.{cust_id} = o.{orders_cust_fk}\n"
                    f"{time_clause}\n"
                    f"GROUP BY c.{cust_id}, c.{cust_name}\n"
                    f"ORDER BY total_spent DESC\n"
                    f"LIMIT 10;"
                )

        # Products / Performance
        if "product" in q_lower or "performing" in q_lower or "best selling" in q_lower:
            if metric == "volume":
                return (
                    f"SELECT p.{prod_id}, p.{prod_name}, SUM(oi.{oi_qty}) AS total_units_sold\n"
                    f"FROM {products_tbl} p\n"
                    f"JOIN {details_tbl} oi ON p.{prod_id} = oi.{oi_prod_fk}\n"
                    f"GROUP BY p.{prod_id}, p.{prod_name}\n"
                    f"ORDER BY total_units_sold DESC\n"
                    f"LIMIT 10;"
                )
            else:
                return (
                    f"SELECT p.{prod_id}, p.{prod_name}, SUM(oi.{oi_qty} * oi.{oi_price}) AS total_revenue\n"
                    f"FROM {products_tbl} p\n"
                    f"JOIN {details_tbl} oi ON p.{prod_id} = oi.{oi_prod_fk}\n"
                    f"GROUP BY p.{prod_id}, p.{prod_name}\n"
                    f"ORDER BY total_revenue DESC\n"
                    f"LIMIT 10;"
                )

        # Sales / Revenue summary
        if "sales" in q_lower or "revenue" in q_lower:
            if "category" in q_lower or (resolved_specification and "category" in resolved_specification.lower()):
                return (
                    f"SELECT p.{prod_category}, SUM(oi.{oi_qty} * oi.{oi_price}) AS category_revenue\n"
                    f"FROM {products_tbl} p\n"
                    f"JOIN {details_tbl} oi ON p.{prod_id} = oi.{oi_prod_fk}\n"
                    f"GROUP BY p.{prod_category}\n"
                    f"ORDER BY category_revenue DESC\n"
                    f"LIMIT 20;"
                )
            return f"SELECT COUNT({order_pk}) AS total_orders, SUM({orders_total}) AS gross_revenue, AVG({orders_total}) AS avg_order_value FROM {orders_tbl};"

        # Recent orders
        if "order" in q_lower and ("recent" in q_lower or "latest" in q_lower):
            return f"SELECT * FROM {orders_tbl} ORDER BY order_date DESC LIMIT 20;"

        # Default fallback: inspect first table in schema
        if table_names:
            first_tbl = sorted(list(table_names))[0]
            return f"SELECT * FROM {first_tbl} LIMIT 25;"

        return "SELECT 1 AS status;"

sql_generator = SQLGenerator()
