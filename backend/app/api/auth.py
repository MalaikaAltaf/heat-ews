from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Site
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user, require_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)
    role: str = Field(default="hse_officer")  # hse_officer, public_health_viewer, data_steward
    permitted_site_id: Optional[str] = None  # e.g., AD_SITE_01, AD_SITE_02, AD_SITE_03


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    permitted_site_id: Optional[str] = None


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(subject=user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "permitted_site_id": user.permitted_site_id
    }


@router.post("/register", response_model=TokenResponse)
def register(reg_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new HSE Officer, Public Health Viewer, or Data Steward.
    Validates site scope assignments against registered Abu Dhabi pilot sites.
    """
    existing = db.query(User).filter(User.username == reg_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists. Please choose a different username."
        )

    # Validate site scoping for HSE Officer
    if reg_data.role == "hse_officer" and reg_data.permitted_site_id:
        site = db.query(Site).filter(Site.site_id == reg_data.permitted_site_id).first()
        if not site:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid site_id '{reg_data.permitted_site_id}'. Must be a valid pilot site."
            )

    new_user = User(
        username=reg_data.username,
        role=reg_data.role,
        permitted_site_id=reg_data.permitted_site_id if reg_data.role == "hse_officer" else None,
        hashed_password=get_password_hash(reg_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(subject=new_user.username)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.user_id,
        "username": new_user.username,
        "role": new_user.role,
        "permitted_site_id": new_user.permitted_site_id
    }


@router.get("/me")
def get_me(user: User = Depends(require_user)):
    return {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "permitted_site_id": user.permitted_site_id
    }


@router.get("/demo-accounts")
def list_demo_accounts():
    """Returns the predefined test accounts specified in SRS v3.0."""
    return [
        {"username": "hse_reem", "role": "HSE Officer (Al Reem)", "site_id": "AD_SITE_01", "password": "password123"},
        {"username": "hse_mussafah", "role": "HSE Officer (Mussafah)", "site_id": "AD_SITE_02", "password": "password123"},
        {"username": "hse_khalifa", "role": "HSE Officer (Khalifa City)", "site_id": "AD_SITE_03", "password": "password123"},
        {"username": "public_health_viewer", "role": "District / Public Health", "site_id": "All Sites", "password": "password123"},
        {"username": "admin_steward", "role": "Data Steward / Admin", "site_id": "All Sites", "password": "password123"},
    ]
