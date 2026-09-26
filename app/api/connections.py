"""
Database Connection Management Endpoints for Multi-Tenant SaaS.
Provides tenant-isolated connection CRUD, credentials encryption, live testing,
and dynamic schema introspection.
"""

import json
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User, Organization, DatabaseConnection
from app.intent.models import (
    CreateConnectionRequest,
    TestConnectionRequest,
    ConnectionResponse
)
from app.core.auth import get_current_user, get_current_organization, require_role
from app.core.security import encrypt_credential, decrypt_credential
from app.services.connection_service import connection_service

router = APIRouter(prefix="/connections", tags=["Database Connections"])

@router.post("", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_connection(
    payload: CreateConnectionRequest,
    current_user: User = Depends(require_role(["owner", "admin"])),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Saves a new database connection for the tenant.
    Validates host against SSRF and encrypts credentials at rest with AES-256-GCM.
    """
    # 1. Encrypt password
    encrypted_pwd = encrypt_credential(payload.password)

    # 2. Create model
    conn = DatabaseConnection(
        organization_id=org.id,
        name=payload.name.strip(),
        db_type=payload.db_type.lower().strip(),
        host=payload.host.strip(),
        port=payload.port,
        database_name=payload.database_name.strip(),
        username=payload.username.strip(),
        encrypted_password=encrypted_pwd,
        ssl_enabled=payload.ssl_enabled
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)

    # 3. Attempt initial schema introspection asynchronously/inline
    try:
        schema = connection_service.introspect_schema(conn)
        conn.schema_cache = json.dumps(schema)
        conn.last_synced_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(conn)
    except Exception as e:
        print(f"[Schema Introspection Notice] Initial auto-introspection skipped: {e}")

    return conn.to_safe_dict()

@router.get("", response_model=List[ConnectionResponse])
def list_connections(
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Lists all database connections belonging strictly to the authenticated tenant."""
    conns = db.query(DatabaseConnection).filter(
        DatabaseConnection.organization_id == org.id
    ).order_by(DatabaseConnection.created_at.desc()).all()
    return [c.to_safe_dict() for c in conns]

@router.get("/{connection_id}", response_model=ConnectionResponse)
def get_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Returns connection details with credentials strictly omitted."""
    conn = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.organization_id == org.id
    ).first()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database connection not found.")
    return conn.to_safe_dict()

@router.delete("/{connection_id}")
def delete_connection(
    connection_id: str,
    current_user: User = Depends(require_role(["owner", "admin"])),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Deletes a database connection."""
    conn = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.organization_id == org.id
    ).first()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database connection not found.")
    db.delete(conn)
    db.commit()
    return {"status": "success", "message": f"Connection '{conn.name}' deleted successfully."}

@router.post("/test")
def test_unsaved_connection(
    payload: TestConnectionRequest,
    current_user: User = Depends(get_current_user)
):
    """Tests database connectivity for unsaved connection credentials."""
    success, err = connection_service.test_connection(
        db_type=payload.db_type,
        host=payload.host,
        port=payload.port,
        database_name=payload.database_name,
        username=payload.username,
        password=payload.password,
        ssl_enabled=payload.ssl_enabled
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    return {"status": "success", "message": "Connection test successful."}

@router.post("/{connection_id}/test")
def test_saved_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Tests connectivity of an existing saved connection."""
    conn = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.organization_id == org.id
    ).first()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database connection not found.")

    raw_pwd = decrypt_credential(conn.encrypted_password)
    success, err = connection_service.test_connection(
        db_type=conn.db_type,
        host=conn.host,
        port=conn.port,
        database_name=conn.database_name,
        username=conn.username,
        password=raw_pwd,
        ssl_enabled=conn.ssl_enabled
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    return {"status": "success", "message": f"Connection '{conn.name}' is healthy and reachable."}

@router.post("/{connection_id}/schema")
@router.get("/{connection_id}/schema")
def introspect_or_get_schema(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Introspects and caches tables, columns, and foreign keys from the connected database.
    Ensures schema belongs strictly to the authenticated tenant.
    """
    conn = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.organization_id == org.id
    ).first()
    if not conn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database connection not found.")

    try:
        schema = connection_service.introspect_schema(conn)
        conn.schema_cache = json.dumps(schema)
        conn.last_synced_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(conn)
        return schema
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to inspect database schema: {str(e)}"
        )
