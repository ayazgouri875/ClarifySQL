"""
SQL Validation and Security Layer.
Enforces read-only safety, table whitelisting, prohibited SQL commands,
statement count checks, and result limit enforcement before execution.
"""

import re
from typing import Tuple, Optional, Set
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import Keyword, DML

from app.database.metadata import get_table_names, get_columns_for_table
from app.core.config import settings

# Explicitly allowed SQL commands
ALLOWED_STATEMENTS = {"SELECT"}

# Prohibited destructive or mutating keywords
FORBIDDEN_KEYWORDS = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE", "CALL",
    "CREATE", "REPLACE", "LOCK", "SHUTDOWN", "ATTACH", "DETACH"
}

class SQLValidator:
    def __init__(self):
        self.valid_tables: Set[str] = set(get_table_names())

    def validate_and_sanitize(
        self,
        sql: str,
        allowed_tables: Optional[Set[str]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates SQL against safety rules.
        Returns:
            (is_valid: bool, sanitized_sql: Optional[str], error_message: Optional[str])
        """
        if not sql or not sql.strip():
            return False, None, "SQL query cannot be empty."

        clean_sql = sql.strip().rstrip(";")

        # 1. Parse using sqlparse
        parsed = sqlparse.parse(clean_sql)
        if not parsed:
            return False, None, "Unable to parse SQL query syntax."

        # Disallow multiple semicolon-separated statements (prevent injection chaining)
        if len(parsed) > 1:
            return False, None, "Multiple statements in a single query are forbidden for security."

        statement = parsed[0]

        # 2. Check statement type - MUST be SELECT
        stmt_type = statement.get_type()
        if stmt_type.upper() != "SELECT":
            return False, None, f"Dangerous operation detected: only SELECT queries are permitted (got {stmt_type})."

        # 3. Keyword blacklist scan
        sql_upper = clean_sql.upper()
        tokens = re.findall(r"\b[A-Z_]+\b", sql_upper)
        for token in tokens:
            if token in FORBIDDEN_KEYWORDS:
                return False, None, f"Forbidden keyword detected in query: '{token}'."

        # 4. Table whitelisting check against dynamic or default tables
        active_tables = {t.lower() for t in allowed_tables} if allowed_tables else self.valid_tables
        extracted_tables = self._extract_tables(clean_sql)
        for table in extracted_tables:
            if table.lower() not in active_tables:
                return False, None, f"Unknown or unauthorized table referenced: '{table}'."

        # 5. Result row limit safety enforcement
        sanitized_sql = self._enforce_limit(clean_sql)

        return True, sanitized_sql, None

    def _extract_tables(self, sql: str) -> Set[str]:
        """Extracts referenced table names from FROM and JOIN clauses."""
        tables = set()
        # Regex captures identifiers after FROM or JOIN
        matches = re.findall(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
        for match in matches:
            tables.add(match.strip().lower())
        return tables

    def _enforce_limit(self, sql: str) -> str:
        """Ensures the query has a reasonable LIMIT clause to prevent server exhaustion."""
        limit_match = re.search(r"\bLIMIT\s+(\d+)", sql, re.IGNORECASE)
        if limit_match:
            current_limit = int(limit_match.group(1))
            if current_limit > settings.MAX_RESULT_ROWS:
                # Replace with max allowed limit
                return re.sub(r"\bLIMIT\s+\d+", f"LIMIT {settings.MAX_RESULT_ROWS}", sql, flags=re.IGNORECASE)
            return sql
        else:
            # Append default limit
            return f"{sql} LIMIT {settings.DEFAULT_QUERY_LIMIT}"

sql_validator = SQLValidator()
