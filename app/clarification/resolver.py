"""
Intent and Clarification Resolver.
Merges the original user query, detected ambiguity, and selected user clarification
into a resolved, unambiguous intent representation.
"""

from typing import Dict, Any, Optional
from app.intent.models import ParsedIntent, AmbiguityItem

class ClarificationResolver:
    def resolve(
        self,
        original_question: str,
        clarification: AmbiguityItem,
        user_choice: str
    ) -> Dict[str, Any]:
        """
        Merges clarification selection with the original question to form
        an unambiguous query specification for SQL generation.
        """
        resolved_context = {
            "original_question": original_question,
            "clarified_term": clarification.term,
            "selected_option": user_choice,
            "resolved_instruction": ""
        }

        choice_lower = user_choice.lower()

        # Best customers resolution
        if "spending" in choice_lower:
            resolved_context["metric"] = "total_spending"
            resolved_context["aggregation"] = "SUM(orders.total_amount)"
            resolved_context["sort"] = "DESC"
            resolved_context["resolved_instruction"] = "Rank customers by total spending (SUM of order total_amount)."
        elif "orders" in choice_lower:
            resolved_context["metric"] = "order_count"
            resolved_context["aggregation"] = "COUNT(orders.order_id)"
            resolved_context["sort"] = "DESC"
            resolved_context["resolved_instruction"] = "Rank customers by total count of orders placed."
        elif "visits" in choice_lower:
            resolved_context["metric"] = "visit_count"
            resolved_context["aggregation"] = "COUNT(visits.visit_id)"
            resolved_context["sort"] = "DESC"
            resolved_context["resolved_instruction"] = "Rank customers by number of website visits."
        elif "average order" in choice_lower:
            resolved_context["metric"] = "avg_order_value"
            resolved_context["aggregation"] = "AVG(orders.total_amount)"
            resolved_context["sort"] = "DESC"
            resolved_context["resolved_instruction"] = "Rank customers by average order value (AVG of total_amount)."

        # Products performance resolution
        elif "revenue" in choice_lower and "product" in original_question.lower():
            resolved_context["metric"] = "product_revenue"
            resolved_context["aggregation"] = "SUM(order_items.line_total)"
            resolved_context["resolved_instruction"] = "Rank products by total gross sales revenue."
        elif "units" in choice_lower:
            resolved_context["metric"] = "units_sold"
            resolved_context["aggregation"] = "SUM(order_items.quantity)"
            resolved_context["resolved_instruction"] = "Rank products by total units sold."
        elif "profit margin" in choice_lower:
            resolved_context["metric"] = "profit_margin"
            resolved_context["aggregation"] = "SUM(order_items.line_total - (order_items.quantity * products.cost_price))"
            resolved_context["resolved_instruction"] = "Rank products by total gross profit (revenue minus cost price)."
        elif "return rate" in choice_lower:
            resolved_context["metric"] = "lowest_return_rate"
            resolved_context["resolved_instruction"] = "Find products with the lowest return rates."

        # Time resolution
        elif "7 days" in choice_lower:
            resolved_context["time_filter"] = "order_date >= '2026-09-19' AND order_date <= '2026-09-26'"
            resolved_context["resolved_instruction"] = "Filter data to the last 7 days."
        elif "september" in choice_lower or "this month" in choice_lower:
            resolved_context["time_filter"] = "order_date >= '2026-09-01' AND order_date <= '2026-09-30'"
            resolved_context["resolved_instruction"] = "Filter data to this month (September 2026)."
        elif "august" in choice_lower or "last month" in choice_lower:
            resolved_context["time_filter"] = "order_date >= '2026-08-01' AND order_date <= '2026-08-31'"
            resolved_context["resolved_instruction"] = "Filter data to last month (August 2026)."
        else:
            resolved_context["resolved_instruction"] = f"Clarified specification: {user_choice}"

        return resolved_context

clarification_resolver = ClarificationResolver()
