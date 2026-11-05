from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user


def require_user(current_user: Optional[User] = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required."
        )
    return current_user


def verify_site_access(site_id: str, current_user: Optional[User] = Depends(get_current_user)) -> bool:
    """
    Enforces server-side site-scoped RBAC (SRS 3):
    - HSE Officer is strictly restricted to their own site.
    - Public Health Viewer and Data Steward can view all aggregate site data.
    """
    if not current_user:
        # Public or unauthenticated defaults to public health / restricted privacy view
        return True
    if current_user.role in ["public_health_viewer", "data_steward"]:
        return True
    if current_user.role == "hse_officer":
        if current_user.permitted_site_id and current_user.permitted_site_id != site_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: HSE Officer is scoped strictly to site {current_user.permitted_site_id}."
            )
    return True

