"""
Safe Read-Only SQL Query Executor.
Executes queries against tenant database connections with safety timeouts and result limits.
"""

import time
import re
from typing import Dict, Any, Tuple
from sqlalchemy import text
from django.conf import settings
from connections.services import get_engine_for_connection
from .sql_validator import sql_validator

class SQLExecutor:
    def execute(self, connection_instance, sql_query: str) -> Dict[str, Any]:
        """Executes a validated read-only SQL query safely."""
        # 1. Validate SQL
        valid, err = sql_validator.validate(sql_query)
        if not valid:
            return {
                "success": False,
                "error": err,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0.0
            }

        # 2. Inject LIMIT if missing
        safe_sql = self._enforce_limit(sql_query)

        # 3. Execute with timeout
        engine = get_engine_for_connection(connection_instance)
        start_time = time.perf_counter()

        try:
            with engine.connect() as conn:
                result = conn.execute(text(safe_sql))
                columns = list(result.keys())
                raw_rows = result.fetchall()
                execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

                # Format rows as list of dicts, converting non-serializable objects
                rows = []
                for r in raw_rows:
                    row_dict = {}
                    for col, val in zip(columns, r):
                        if val is None:
                            row_dict[col] = None
                        elif isinstance(val, (int, float, bool, str)):
                            row_dict[col] = val
                        else:
                            row_dict[col] = str(val)
                    rows.append(row_dict)

                return {
                    "success": True,
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows),
                    "execution_time_ms": execution_time_ms,
                    "executed_sql": safe_sql
                }
        except Exception as exc:
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "success": False,
                "error": str(exc),
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": execution_time_ms,
                "executed_sql": safe_sql
            }
        finally:
            engine.dispose()

    def _enforce_limit(self, sql_query: str) -> str:
        clean = sql_query.strip().rstrip(";")
        max_rows = getattr(settings, "MAX_RESULT_ROWS", 1000)
        default_limit = getattr(settings, "DEFAULT_QUERY_LIMIT", 50)

        # Check if LIMIT already present
        limit_match = re.search(r"\bLIMIT\s+(\d+)\b", clean, flags=re.IGNORECASE)
        if limit_match:
            existing_limit = int(limit_match.group(1))
            if existing_limit > max_rows:
                # Cap to max_rows
                clean = re.sub(r"\bLIMIT\s+\d+\b", f"LIMIT {max_rows}", clean, flags=re.IGNORECASE)
            return clean + ";"
        else:
            return f"{clean} LIMIT {default_limit};"

sql_executor = SQLExecutor()
