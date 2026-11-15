from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, security_bearer, decode_access_token
from app.models.models import User, Organisation
from app.schemas.schemas import LoginRequest, TokenSchema, UserOut
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_current_user(token = Depends(security_bearer), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication credentials required")
    payload = decode_access_token(token.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user

def require_role(roles: list):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(roles)}"
            )
        return current_user
    return role_checker

@router.post("/login", response_model=TokenSchema)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "org_id": user.org_id})
    user_data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "department": user.department,
        "org_id": user.org_id,
        "avatar_url": user.avatar_url
    }
    return {"access_token": access_token, "token_type": "bearer", "user": user_data}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
        "org_id": current_user.org_id,
        "avatar_url": current_user.avatar_url,
        "organisation_name": current_user.organisation.name if current_user.organisation else "Default Org"
    }

@router.post("/demo-switch")
def demo_switch(role: str, db: Session = Depends(get_db)):
    """One-click demo role switcher for judges and testers (ADMIN, CREATOR, REVIEWER)."""
    target_role = role.upper()
    if target_role not in ("ADMIN", "CREATOR", "REVIEWER"):
        raise HTTPException(status_code=400, detail="Invalid role. Must be ADMIN, CREATOR, or REVIEWER.")
        
    user = db.query(User).filter(User.role == target_role).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"No pre-configured demo user found for role {target_role}")
        
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "org_id": user.org_id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "org_id": user.org_id,
            "avatar_url": user.avatar_url,
            "organisation_name": user.organisation.name if user.organisation else "Default Org"
        }
    }
