"""FastAPI dependencies for authentication and authorization"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.database import Database

from backend.database import get_db_mongo
from backend.database import crud
from backend.auth.auth_handler import verify_token

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_db_mongo)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user
    
    Usage in route:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"username": current_user.username}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    username = verify_token(token, token_type="access")
    
    if username is None:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to require admin role
    
    Usage in route:
        @app.delete("/users/{user_id}")
        def delete_user(user_id: int, admin: User = Depends(get_current_active_admin)):
            ...
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Database = Depends(get_db_mongo)
) -> Optional[Dict[str, Any]]:
    """
    Dependency to get current user if authenticated, otherwise None
    Useful for endpoints that work with or without authentication
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    username = verify_token(token, token_type="access")
    
    if username is None:
        return None
    
    user = crud.get_user_by_username(db, username=username)
    return user if user and user.get("is_active", True) else None
