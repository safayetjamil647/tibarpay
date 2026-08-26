from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import decode_access_token
from app.models import User
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_admin(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    is_admin = db.query(models.Role).join(models.user_roles).filter(
        models.user_roles.c.user_id == current_user.id,
        models.Role.name.in_(["Admin", "Maker Admin", "Checker Admin", "Super Admin"])
    ).first()
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

def check_permission(permission_name: str):
    def dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # Check if user has role with the given permission name
        has_perm = db.query(models.Permission).join(models.role_permissions).join(models.Role).join(models.user_roles).filter(
            models.user_roles.c.user_id == current_user.id,
            models.Permission.name == permission_name
        ).first()
        
        # Super admin role "Admin" and "Super Admin" have all permissions implicitly
        is_super_admin = db.query(models.Role).join(models.user_roles).filter(
            models.user_roles.c.user_id == current_user.id,
            models.Role.name.in_(["Admin", "Super Admin"])
        ).first()
        
        if not has_perm and not is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_name}"
            )
        return current_user
    return dependency
