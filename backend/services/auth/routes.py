"""Authentication API routes"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from backend.shared.database import get_db_mongo, crud, models
from backend.shared.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_password_hash
)
from backend.shared.models.schemas import UserLogin, UserRegister, UserResponse, Token, TokenRefresh
from backend.shared.config import settings
from backend.shared.utils.logging_utils import send_log

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Database = Depends(get_db_mongo)):
    """
    Register a new user account
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Minimum 6 characters
    """
    # Check if username exists
    if crud.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if crud.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user (password will be hashed in crud)
    # The original code imported get_password_hash locally inside the function.
    # We imported it at the top level now from shared.auth.
    hashed_password = get_password_hash(user_data.password)
    
    user = crud.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role="user"
    )
    
    send_log(f"New user registered: {user_data.username}", "info")
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Database = Depends(get_db_mongo)):
    """
    Login with username and password to get JWT tokens
    
    Returns access token (30 min) and refresh token (7 days)
    """
    # Get user from database
    user = crud.get_user_by_username(db, credentials.username)
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        send_log(f"Failed login attempt for username: {credentials.username}", "warning")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    crud.update_user_last_login(db, str(user["_id"]))
    
    # Create tokens
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    send_log(f"User logged in: {user['username']}", "info")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Database = Depends(get_db_mongo)):
    """
    Get a new access token using a refresh token
    """
    username = verify_token(token_data.refresh_token, token_type="refresh")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.get_user_by_username(db, username)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return UserResponse.from_mongo(current_user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (client should discard tokens)
    
    Note: With JWT, actual logout happens client-side by deleting tokens.
    This endpoint is provided for consistency and future session management.
    """
    return {"message": "Successfully logged out"}
