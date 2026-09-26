"""
Organization Management Endpoints.
Allows tenants to inspect and manage their organization workspace.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User, Organization, DatabaseConnection
from app.intent.models import UpdateOrganizationRequest
from app.core.auth import get_current_user, get_current_organization, require_role

router = APIRouter(prefix="/organization", tags=["Organization"])

@router.get("")
def get_organization_details(
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """
    Returns current organization details with counts of connected databases and members.
    """
    connection_count = db.query(DatabaseConnection).filter(
        DatabaseConnection.organization_id == org.id
    ).count()
    member_count = db.query(User).filter(User.organization_id == org.id).count()

    res = org.to_dict()
    res.update({
        "connection_count": connection_count,
        "member_count": member_count
    })
    return res

@router.patch("")
def update_organization(
    payload: UpdateOrganizationRequest,
    current_user: User = Depends(require_role(["owner", "admin"])),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Updates organization workspace details (Admin or Owner only)."""
    org.name = payload.name.strip()
    db.commit()
    db.refresh(org)
    return org.to_dict()
