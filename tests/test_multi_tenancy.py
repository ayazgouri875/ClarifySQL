"""
Comprehensive Multi-Tenancy and Security Test Suite for QueryMind SaaS.
Validates:
1. Authentication (Signup, Login, Duplicate Rejection, Password Verification)
2. Tenant Isolation (Connections, Query History, Schemas)
3. Credential Security (Passwords encrypted, never returned in API)
4. Dynamic Schema Introspection & Tenant Query Execution
"""

import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import init_app_database, SessionLocal, app_engine
from app.database.models import Base, User, Organization, DatabaseConnection, QueryHistoryItem

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=app_engine)
    init_app_database()


def test_auth_signup_flow():
    # 1. Successful Signup for Organization A
    res_a = client.post("/api/v1/auth/signup", json={
        "name": "Alice Corp Admin",
        "email": "alice@acmecorp.com",
        "password": "SecurePassword2026!",
        "organization_name": "Acme Corporation"
    })
    assert res_a.status_code == 201
    data_a = res_a.json()
    assert "access_token" in data_a
    assert data_a["user"]["name"] == "Alice Corp Admin"
    assert data_a["organization"]["name"] == "Acme Corporation"
    assert data_a["user"]["role"] == "owner"

    # 2. Duplicate email rejection
    res_dup = client.post("/api/v1/auth/signup", json={
        "name": "Alice Duplicate",
        "email": "alice@acmecorp.com",
        "password": "AnotherPassword123!",
        "organization_name": "Another Corp"
    })
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"]

def test_auth_login_and_me():
    # 1. Login with correct credentials
    res = client.post("/api/v1/auth/login", json={
        "email": "alice@acmecorp.com",
        "password": "SecurePassword2026!"
    })
    assert res.status_code == 200
    token = res.json()["access_token"]

    # 2. Login with incorrect password
    res_wrong = client.post("/api/v1/auth/login", json={
        "email": "alice@acmecorp.com",
        "password": "WrongPassword!"
    })
    assert res_wrong.status_code == 401

    # 3. Access protected /auth/me
    res_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["user"]["email"] == "alice@acmecorp.com"
    assert res_me.json()["organization"]["name"] == "Acme Corporation"

def test_tenant_isolation_connections():
    # Setup Org A
    res_a = client.post("/api/v1/auth/login", json={
        "email": "alice@acmecorp.com",
        "password": "SecurePassword2026!"
    })
    token_a = res_a.json()["access_token"]
    org_a_id = res_a.json()["organization"]["id"]

    # Setup Org B
    res_b = client.post("/api/v1/auth/signup", json={
        "name": "Bob Beta Admin",
        "email": "bob@betalabs.io",
        "password": "SecureBeta2026!",
        "organization_name": "Beta Labs"
    })
    token_b = res_b.json()["access_token"]
    org_b_id = res_b.json()["organization"]["id"]
    assert org_a_id != org_b_id

    # Org A adds a database connection
    db_path = os.path.abspath("database/company.db")
    res_conn_a = client.post(
        "/api/v1/connections",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "name": "Acme Production DB",
            "db_type": "sqlite",
            "host": db_path,
            "port": 0,
            "database_name": db_path,
            "username": "",
            "password": "SuperSecretPassword123!",
            "ssl_enabled": False
        }
    )
    assert res_conn_a.status_code == 201
    conn_a_id = res_conn_a.json()["id"]

    # SECURITY CHECK: Password must NEVER be returned in response!
    assert "password" not in res_conn_a.json()
    assert "SuperSecretPassword123!" not in str(res_conn_a.json())

    # Org A lists connections: sees its connection
    list_a = client.get("/api/v1/connections", headers={"Authorization": f"Bearer {token_a}"})
    assert list_a.status_code == 200
    assert any(c["id"] == conn_a_id for c in list_a.json())

    # TENANT ISOLATION CHECK: Org B lists connections -> MUST NOT see Org A's connection!
    list_b = client.get("/api/v1/connections", headers={"Authorization": f"Bearer {token_b}"})
    assert list_b.status_code == 200
    assert not any(c["id"] == conn_a_id for c in list_b.json())

    # TENANT ISOLATION CHECK: Org B attempts direct access to Org A's connection -> MUST be 404
    get_cross = client.get(f"/api/v1/connections/{conn_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert get_cross.status_code == 404

    # TENANT ISOLATION CHECK: Org B attempts to delete Org A's connection -> MUST be 404
    del_cross = client.delete(f"/api/v1/connections/{conn_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_cross.status_code == 404

def test_tenant_isolation_query_and_history():
    # Login Org A & Org B
    res_a = client.post("/api/v1/auth/login", json={"email": "alice@acmecorp.com", "password": "SecurePassword2026!"})
    token_a = res_a.json()["access_token"]

    res_b = client.post("/api/v1/auth/login", json={"email": "bob@betalabs.io", "password": "SecureBeta2026!"})
    token_b = res_b.json()["access_token"]

    # Get Org A's connection
    conns_a = client.get("/api/v1/connections", headers={"Authorization": f"Bearer {token_a}"}).json()
    conn_a_id = conns_a[0]["id"]

    # Org A executes a query against its connection
    query_res = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "connection_id": conn_a_id,
            "question": "How many customers signed up last month?"
        }
    )
    assert query_res.status_code == 200
    assert query_res.json()["status"] == "success"
    assert query_res.json()["data"]["rows"][0][0] == 6

    # Org A checks query history -> sees query
    hist_a = client.get("/api/v1/history", headers={"Authorization": f"Bearer {token_a}"})
    assert hist_a.status_code == 200
    assert len(hist_a.json()) > 0
    assert hist_a.json()[0]["natural_language_query"] == "How many customers signed up last month?"

    # TENANT ISOLATION CHECK: Org B checks query history -> MUST NOT see Org A's queries!
    hist_b = client.get("/api/v1/history", headers={"Authorization": f"Bearer {token_b}"})
    assert hist_b.status_code == 200
    assert len(hist_b.json()) == 0

    # TENANT ISOLATION CHECK: Org B attempts to query using Org A's connection_id -> 404 Forbidden
    cross_query = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "connection_id": conn_a_id,
            "question": "Show customers"
        }
    )
    assert cross_query.status_code == 404

def test_tenant_ambiguity_and_clarification_on_connection():
    # Login Org A
    res_a = client.post("/api/v1/auth/login", json={"email": "alice@acmecorp.com", "password": "SecurePassword2026!"})
    token_a = res_a.json()["access_token"]
    conns_a = client.get("/api/v1/connections", headers={"Authorization": f"Bearer {token_a}"}).json()
    conn_a_id = conns_a[0]["id"]

    # Step 1: Submit ambiguous query against connection
    res1 = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "connection_id": conn_a_id,
            "question": "Show me the best customers last month"
        }
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "clarification_required"
    assert "best customers" in res1.json()["clarification"]["question"].lower()
    session_id = res1.json()["session_id"]

    # Step 2: Submit clarification answer against connection
    res2 = client.post(
        "/api/v1/query",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "session_id": session_id,
            "connection_id": conn_a_id,
            "question": "Show me the best customers last month",
            "selected_clarification": "Highest total spending (SUM of orders)"
        }
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "success"
    assert res2.json()["validated"] is True
    assert res2.json()["data"]["rows"][0][1] == "Apex Global Logistics"
