"""
Natural Language Query and Clarification Endpoints.
Dispatches queries to the dynamic schema-aware Text-to-SQL pipeline and enforces tenant isolation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User, Organization, DatabaseConnection
from app.intent.models import QueryRequest, QueryResponse
from app.core.auth import oauth2_scheme
from app.core.security import decode_token
from app.services.query_service import query_service

router = APIRouter(prefix="/query", tags=["Query Engine"])

def get_optional_auth_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Helper for endpoints supporting both authenticated tenant queries and demo access."""
    if not token:
        return None
    try:
        payload = decode_token(token, is_refresh=False)
        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        if user_id and org_id:
            return db.query(User).filter(User.id == user_id, User.organization_id == org_id).first()
    except Exception:
        return None
    return None

@router.post("", response_model=QueryResponse)
def execute_nl_query(
    request: QueryRequest,
    current_user: Optional[User] = Depends(get_optional_auth_user),
    db: Session = Depends(get_db)
):
    """
    Submits a natural language query or clarification response.
    If authenticated and connection_id is supplied, isolates execution to the tenant's database.
    """
    target_connection = None

    if request.connection_id:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required to query custom database connections."
            )
        
        # Verify connection belongs strictly to this tenant
        target_connection = db.query(DatabaseConnection).filter(
            DatabaseConnection.id == request.connection_id,
            DatabaseConnection.organization_id == current_user.organization_id
        ).first()

        if not target_connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database connection not found or does not belong to your organization."
            )

    response = query_service.process_query(
        request=request,
        organization_id=current_user.organization_id if current_user else None,
        user_id=current_user.id if current_user else None,
        connection=target_connection,
        db=db if current_user else None
    )

    return response

@router.post("/clarify", response_model=QueryResponse)
def clarify_query(
    request: QueryRequest,
    current_user: Optional[User] = Depends(get_optional_auth_user),
    db: Session = Depends(get_db)
):
    """Alias endpoint for clarification answer submissions."""
    return execute_nl_query(request=request, current_user=current_user, db=db)

@router.post("/execute", response_model=QueryResponse)
def direct_execute_query(
    request: QueryRequest,
    current_user: Optional[User] = Depends(get_optional_auth_user),
    db: Session = Depends(get_db)
):
    """Alias endpoint for direct query execution."""
    return execute_nl_query(request=request, current_user=current_user, db=db)
