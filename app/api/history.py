"""
Query History Endpoints for Multi-Tenant SaaS.
Provides tenant-isolated audit logs of natural language questions,
clarification interactions, generated SQL, and execution metrics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User, Organization, QueryHistoryItem
from app.core.auth import get_current_user, get_current_organization

router = APIRouter(prefix="/history", tags=["Query History"])

@router.get("")
def list_tenant_query_history(
    connection_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Returns query history records strictly belonging to the authenticated tenant.
    Never exposes queries from other organizations.
    """
    query = db.query(QueryHistoryItem).filter(
        QueryHistoryItem.organization_id == org.id
    )

    if connection_id:
        query = query.filter(QueryHistoryItem.connection_id == connection_id)

    items = query.order_by(QueryHistoryItem.created_at.desc()).limit(limit).all()
    return [i.to_dict() for i in items]

@router.get("/{history_id}")
def get_history_item(
    history_id: str,
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Returns details for a specific query log if it belongs to the tenant."""
    item = db.query(QueryHistoryItem).filter(
        QueryHistoryItem.id == history_id,
        QueryHistoryItem.organization_id == org.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query history item not found."
        )
    return item.to_dict()

@router.delete("/{history_id}")
def delete_history_item(
    history_id: str,
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Deletes a query history item belonging to the tenant."""
    item = db.query(QueryHistoryItem).filter(
        QueryHistoryItem.id == history_id,
        QueryHistoryItem.organization_id == org.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query history item not found."
        )
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "History item deleted."}
