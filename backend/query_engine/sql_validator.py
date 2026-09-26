"""
SQL Security and Syntax Validator.
Enforces read-only database execution, prevents stacked queries, and verifies statement safety.
"""

from typing import Tuple, Optional
import re
import sqlparse

FORBIDDEN_KEYWORDS = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "REPLACE",
    "MERGE", "CALL", "UPSERT", "ATTACH", "DETACH"
}

class SQLValidator:
    def validate(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        if not sql_query or not sql_query.strip():
            return False, "Query cannot be empty."

        clean = sql_query.strip()

        # Parse with sqlparse
        parsed = sqlparse.parse(clean)
        if not parsed:
            return False, "Failed to parse SQL statement."

        if len(parsed) > 1:
            return False, "Multiple SQL statements are strictly forbidden. Only single queries are permitted."

        stmt = parsed[0]
        first_token = stmt.get_type()

        # Only SELECT queries are permitted
        if first_token not in ("SELECT", "UNKNOWN"):
            return False, f"Only SELECT statements are permitted. Statement type '{first_token}' is rejected."

        # Check raw text for forbidden keyword boundaries
        sql_upper = clean.upper()
        for kw in FORBIDDEN_KEYWORDS:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, sql_upper):
                return False, f"Security violation: Forbidden keyword '{kw}' detected. Only read-only queries are permitted."

        return True, None

sql_validator = SQLValidator()
