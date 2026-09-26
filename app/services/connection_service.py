"""
Database Connection and Schema Introspection Service.
Handles credential encryption, SSRF validation, connection testing,
live schema introspection (tables, columns, types, foreign keys),
and isolated read-only query execution.
"""

import json
import time
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.security import encrypt_credential, decrypt_credential, validate_host_safety
from app.database.models import DatabaseConnection

class ConnectionService:
    def build_connection_url(
        self,
        db_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str,
        ssl_enabled: bool = False
    ) -> str:
        """Constructs an encrypted connection URL for SQLAlchemy."""
        db_type_lower = db_type.lower().strip()
        encoded_user = urllib.parse.quote_plus(username)
        encoded_pass = urllib.parse.quote_plus(password)

        if db_type_lower == "postgresql":
            url = f"postgresql+psycopg2://{encoded_user}:{encoded_pass}@{host}:{port}/{database_name}"
            if ssl_enabled:
                url += "?sslmode=require"
            return url
        elif db_type_lower == "mysql":
            url = f"mysql+pymysql://{encoded_user}:{encoded_pass}@{host}:{port}/{database_name}"
            if ssl_enabled:
                url += "?ssl=true"
            return url
        elif db_type_lower == "sqlite":
            # For SQLite (primarily local test databases)
            return f"sqlite:///{host if host.endswith('.db') else database_name}"
        else:
            raise ValueError(f"Unsupported database type: '{db_type}'. Supported: 'postgresql', 'mysql', 'sqlite'.")

    def test_connection(
        self,
        db_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str,
        ssl_enabled: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates host safety against SSRF and tests connection with a lightweight 'SELECT 1;' query.
        Returns: (success: bool, error_message: Optional[str])
        """
        # SSRF check
        if db_type.lower() != "sqlite":
            safe, err = validate_host_safety(host, port)
            if not safe:
                return False, err

        try:
            url = self.build_connection_url(
                db_type=db_type,
                host=host,
                port=port,
                database_name=database_name,
                username=username,
                password=password,
                ssl_enabled=ssl_enabled
            )
            
            engine = create_engine(
                url,
                connect_args={"connect_timeout": 5} if "sqlite" not in url else {},
                pool_pre_ping=True
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
            engine.dispose()
            return True, None
        except Exception as e:
            # Mask sensitive internal network / credential details
            print(f"[ConnectionService Error] Connection test failed: {e}")
            return False, "Unable to establish database connection. Please verify the host, port, credentials, and SSL settings."

    def introspect_schema(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """
        Introspects tables, columns, data types, primary keys, and foreign keys
        from the customer's live database connection.
        """
        raw_password = decrypt_credential(connection.encrypted_password)
        url = self.build_connection_url(
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=raw_password,
            ssl_enabled=connection.ssl_enabled
        )

        engine = create_engine(
            url,
            connect_args={"connect_timeout": 8} if "sqlite" not in url else {},
            pool_pre_ping=True
        )

        schema_result = {"tables": {}}

        try:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            for table in table_names:
                # Get columns
                cols_meta = {}
                pk_constraint = inspector.get_pk_constraint(table)
                pk_cols = pk_constraint.get("constrained_columns", []) if pk_constraint else []
                primary_key = pk_cols[0] if pk_cols else None

                for col in inspector.get_columns(table):
                    col_name = col["name"]
                    type_str = str(col["type"])
                    nullable = col.get("nullable", True)
                    cols_meta[col_name] = {
                        "type": type_str,
                        "description": f"{'Primary Key, ' if col_name == primary_key else ''}{'Nullable' if nullable else 'Required'}"
                    }

                # Get foreign keys
                fks = []
                for fk in inspector.get_foreign_keys(table):
                    referred_table = fk.get("referred_table")
                    constrained_cols = fk.get("constrained_columns", [])
                    referred_cols = fk.get("referred_columns", [])
                    if constrained_cols and referred_cols:
                        fks.append({
                            "column": constrained_cols[0],
                            "references_table": referred_table,
                            "references_column": referred_cols[0]
                        })

                schema_result["tables"][table] = {
                    "description": f"Table '{table}' with {len(cols_meta)} attributes",
                    "primary_key": primary_key,
                    "columns": cols_meta,
                    "foreign_keys": fks,
                    "synonyms": [table.lower().replace("_", " ")]
                }

        finally:
            engine.dispose()

        return schema_result

    def execute_query(
        self,
        connection: DatabaseConnection,
        sql: str
    ) -> Tuple[List[str], List[List[Any]], float]:
        """
        Executes a validated read-only SQL query on the specified tenant database connection.
        Returns: (columns: List[str], rows: List[List[Any]], execution_time_ms: float)
        """
        raw_password = decrypt_credential(connection.encrypted_password)
        url = self.build_connection_url(
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=raw_password,
            ssl_enabled=connection.ssl_enabled
        )

        engine = create_engine(
            url,
            connect_args={"connect_timeout": settings.QUERY_TIMEOUT_SECONDS} if "sqlite" not in url else {},
            pool_pre_ping=True
        )

        start_time = time.time()
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                columns = list(result.keys())
                rows = [list(row) for row in result.fetchall()]

            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            return columns, rows, execution_time_ms
        finally:
            engine.dispose()

connection_service = ConnectionService()
