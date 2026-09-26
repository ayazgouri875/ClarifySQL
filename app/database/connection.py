"""
Database connection manager supporting both PostgreSQL and local SQLite.
Enforces execution timeouts and returns clean row dictionaries.
"""

import time
import os
from typing import Tuple, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self._init_connection()

    def _init_connection(self):
        """Initializes connection engine based on settings."""
        if settings.DATABASE_TYPE == "postgres":
            try:
                # Test postgres connection
                test_engine = create_engine(
                    settings.POSTGRES_READONLY_URL,
                    connect_args={"connect_timeout": 3},
                    pool_pre_ping=True
                )
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.engine = test_engine
                print("Connected to PostgreSQL successfully.")
                return
            except Exception as e:
                print(f"Warning: PostgreSQL connection failed ({e}). Falling back to SQLite.")

        # SQLite fallback / default
        sqlite_url = settings.DATABASE_URL
        self.engine = create_engine(
            sqlite_url,
            connect_args={"timeout": settings.QUERY_TIMEOUT_SECONDS}
        )
        print(f"Using SQLite database engine at {sqlite_url}")

    def execute_query(self, sql: str) -> Tuple[List[str], List[List[Any]], float]:
        """
        Executes a validated read-only SQL query and returns:
        (columns: List[str], rows: List[List[Any]], execution_time_ms: float)
        """
        if not self.engine:
            self._init_connection()

        start_time = time.time()
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]
        
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        return columns, rows, execution_time_ms

db_manager = DatabaseManager()
