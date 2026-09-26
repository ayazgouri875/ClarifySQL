import logging
from typing import Dict, Any, List
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)

class DatabaseIntrospector:
    """Introspects relational database schemas (SQLite, PostgreSQL, MySQL) using SQLAlchemy."""

    @classmethod
    def introspect(cls, engine) -> Dict[str, Any]:
        inspector = inspect(engine)
        schema_dict = {
            "tables": {},
            "dialect": engine.dialect.name
        }

        table_names = inspector.get_table_names()

        for table_name in table_names:
            try:
                columns_meta = {}
                columns = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                pk_cols = set(pk_constraint.get("constrained_columns", []) if pk_constraint else [])

                for col in columns:
                    col_name = col["name"]
                    columns_meta[col_name] = {
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "primary_key": col_name in pk_cols,
                        "default": str(col.get("default")) if col.get("default") is not None else None
                    }

                # Foreign keys
                foreign_keys = []
                try:
                    fks = inspector.get_foreign_keys(table_name)
                    for fk in fks:
                        constrained = fk.get("constrained_columns", [])
                        referred_table = fk.get("referred_table")
                        referred_cols = fk.get("referred_columns", [])
                        if constrained and referred_table and referred_cols:
                            foreign_keys.append({
                                "column": constrained[0],
                                "references_table": referred_table,
                                "references_column": referred_cols[0]
                            })
                except Exception as fk_err:
                    logger.debug(f"Error fetching FKs for {table_name}: {fk_err}")

                schema_dict["tables"][table_name] = {
                    "columns": columns_meta,
                    "foreign_keys": foreign_keys,
                    "description": f"Table storing {table_name.replace('_', ' ')} records"
                }

            except Exception as tbl_err:
                logger.warning(f"Error introspecting table {table_name}: {tbl_err}")

        return schema_dict

    @classmethod
    def get_sample_rows(cls, engine, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """Fetches sample preview rows from a specific table."""
        # Sanitize table_name to letters, numbers, underscore
        safe_table = "".join(c for c in table_name if c.isalnum() or c == "_")
        if not safe_table:
            return {"columns": [], "rows": []}

        query = f"SELECT * FROM {safe_table} LIMIT :lim"
        with engine.connect() as conn:
            result = conn.execute(text(query), {"lim": limit})
            columns = list(result.keys())
            rows = [dict(zip(columns, [str(v) if v is not None else None for v in row])) for row in result.fetchall()]
            return {"columns": columns, "rows": rows}
