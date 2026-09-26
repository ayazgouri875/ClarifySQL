"""
Comprehensive Unit and Integration Test Suite for QueryMind.
Validates:
1. Schema integrity & metadata
2. Direct clear queries
3. Ambiguity detection
4. Clarification resolution
5. SQL security validation & injection prevention
"""

import pytest
from app.intent.models import QueryRequest
from app.services.query_service import query_service
from app.sql.validator import sql_validator
from app.database.metadata import get_table_names, SCHEMA_METADATA

def test_schema_metadata_integrity():
    tables = get_table_names()
    assert len(tables) == 10
    expected = [
        "employees", "sales_reps", "customers", "products",
        "orders", "order_items", "payments", "visits", "shipments", "returns"
    ]
    for table in expected:
        assert table in tables
        assert len(SCHEMA_METADATA["tables"][table]["columns"]) > 0

def test_direct_clear_query_signups():
    req = QueryRequest(question="How many customers signed up last month?")
    res = query_service.process_query(req)
    assert res.status == "success"
    assert res.generated_sql is not None
    assert "COUNT(*)" in res.generated_sql
    assert res.data is not None
    assert res.data.rows[0][0] == 6  # 6 customers signed up in August 2026

def test_direct_clear_query_city_filter():
    req = QueryRequest(question="Show customers from Mumbai")
    res = query_service.process_query(req)
    assert res.status == "success"
    assert res.data.row_count > 0
    assert "mumbai" in res.generated_sql.lower()

def test_anti_join_never_ordered():
    req = QueryRequest(question="Which customers have never placed an order?")
    res = query_service.process_query(req)
    assert res.status == "success"
    assert res.data.row_count == 12  # exactly 12 never ordered

def test_ambiguity_detection_best_customers():
    req = QueryRequest(question="Show me the best customers last month")
    res = query_service.process_query(req)
    assert res.status == "clarification_required"
    assert res.clarification is not None
    assert res.clarification.category == "metric"
    assert len(res.clarification.options) >= 3

def test_ambiguity_detection_products():
    req = QueryRequest(question="Which products are performing well?")
    res = query_service.process_query(req)
    assert res.status == "clarification_required"
    assert res.clarification.category == "ranking"

def test_ambiguity_detection_recent():
    req = QueryRequest(question="Show recent orders")
    res = query_service.process_query(req)
    assert res.status == "clarification_required"
    assert res.clarification.category == "time"

def test_clarification_resolution_flow():
    # Step 1: Submit ambiguous query
    req1 = QueryRequest(question="Show me the best customers last month")
    res1 = query_service.process_query(req1)
    assert res1.status == "clarification_required"
    session_id = res1.session_id

    # Step 2: Answer with Highest total spending
    req2 = QueryRequest(
        session_id=session_id,
        question="Show me the best customers last month",
        selected_clarification="Highest total spending (SUM of orders)"
    )
    res2 = query_service.process_query(req2)
    assert res2.status == "success"
    assert res2.validated is True
    assert "SUM(o.total_amount)" in res2.generated_sql
    assert res2.data.rows[0][1] == "Apex Global Logistics"

def test_sql_validator_security_rejection():
    # Mutating / destructive commands
    bad_queries = [
        "DROP TABLE customers;",
        "DELETE FROM orders WHERE order_id = 1;",
        "UPDATE employees SET salary = 999999;",
        "INSERT INTO customers (customer_name) VALUES ('Hacker');",
        "TRUNCATE TABLE payments;",
        "ALTER TABLE products DROP COLUMN cost_price;",
        "SELECT * FROM customers; DROP TABLE orders;"
    ]
    for q in bad_queries:
        is_valid, _, err = sql_validator.validate_and_sanitize(q)
        assert is_valid is False, f"Expected query to fail: {q}"
        assert err is not None

def test_sql_validator_table_whitelisting():
    bad_table_query = "SELECT * FROM passwords_table;"
    is_valid, _, err = sql_validator.validate_and_sanitize(bad_table_query)
    assert is_valid is False
    assert "Unknown or unauthorized table" in err

def test_sql_validator_limit_enforcement():
    query_no_limit = "SELECT customer_id, customer_name FROM customers"
    is_valid, sanitized, _ = sql_validator.validate_and_sanitize(query_no_limit)
    assert is_valid is True
    assert "LIMIT" in sanitized
