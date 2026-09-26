"""
Authentication Endpoints for QueryMind Multi-Tenant SaaS.
Provides signup, login, refresh, logout, and current user profile endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import User, Organization
from app.intent.models import (
    SignUpRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.auth import get_current_user, get_current_organization

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    """
    Registers a new tenant organization and owner user account.
    Returns access and refresh JWT tokens.
    """
    email_clean = payload.email.lower().strip()

    # Check if user already exists
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # 1. Create Organization
    org = Organization(name=payload.organization_name.strip())
    db.add(org)
    db.flush()

    # 2. Create Owner User
    hashed_pwd = hash_password(payload.password)
    user = User(
        organization_id=org.id,
        name=payload.name.strip(),
        email=email_clean,
        password_hash=hashed_pwd,
        role="owner"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(org)

    # 3. Generate Tokens
    token_claims = {
        "sub": user.id,
        "org_id": org.id,
        "role": user.role
    }
    access_token = create_access_token(token_claims)
    refresh_token = create_refresh_token(token_claims)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict(),
        organization=org.to_dict()
    )

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns access/refresh JWT tokens.
    """
    email_clean = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    org = db.query(Organization).filter(Organization.id == user.organization_id).first()

    token_claims = {
        "sub": user.id,
        "org_id": user.organization_id,
        "role": user.role
    }
    access_token = create_access_token(token_claims)
    refresh_token = create_refresh_token(token_claims)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict(),
        organization=org.to_dict() if org else {}
    )

@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Issues a new access token using a valid refresh token.
    """
    try:
        claims = decode_token(payload.refresh_token, is_refresh=True)
        user_id = claims.get("sub")
        org_id = claims.get("org_id")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user = db.query(User).filter(User.id == user_id, User.organization_id == org_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")

    new_claims = {
        "sub": user.id,
        "org_id": user.organization_id,
        "role": user.role
    }
    new_access_token = create_access_token(new_claims)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout():
    """Client logout confirmation."""
    return {"status": "success", "message": "Successfully logged out."}

@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_organization)
):
    """
    Returns the authenticated user profile and organization details.
    """
    return {
        "user": current_user.to_dict(),
        "organization": org.to_dict()
    }
