"""
SQL Executor Service.
Combines validation and execution with standardized error handling.
"""

from typing import Tuple, Optional
from app.sql.validator import sql_validator
from app.database.connection import db_manager
from app.intent.models import QueryResultData

class SQLExecutor:
    def __init__(self):
        self.validator = sql_validator
        self.db = db_manager

    def execute_safe_sql(self, sql: str) -> Tuple[bool, Optional[QueryResultData], Optional[str], Optional[str]]:
        """
        Validates, sanitizes, and executes SQL.
        Returns:
            (success: bool, data: Optional[QueryResultData], sanitized_sql: Optional[str], error_message: Optional[str])
        """
        # Step 1: Validation & Sanitization
        is_valid, sanitized_sql, error_msg = self.validator.validate_and_sanitize(sql)
        if not is_valid:
            return False, None, None, error_msg

        # Step 2: Database Execution
        try:
            columns, rows, exec_ms = self.db.execute_query(sanitized_sql)
            result_data = QueryResultData(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=exec_ms
            )
            return True, result_data, sanitized_sql, None
        except Exception as e:
            # Mask sensitive internal stack traces from raw DB errors
            clean_error = f"Database execution error: {str(e)}"
            return False, None, sanitized_sql, clean_error

sql_executor = SQLExecutor()
