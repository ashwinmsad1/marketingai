"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from backend.app.dependencies import get_db, get_current_active_user
from backend.auth import authenticate_user, create_tokens
from backend.auth.models import UserRegister, UserProfile, Token
from backend.database.models import User

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """User login"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    tokens = create_tokens(user.id)
    return tokens


@router.post("/register", response_model=UserProfile)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """User registration"""
    # Implementation from existing auth module
    pass


@router.post("/refresh")
async def refresh_token(
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token"""
    # Implementation from existing auth module
    pass


@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """User logout"""
    return {"message": "Successfully logged out"}


@router.post("/verify-email")
async def verify_email(
    db: Session = Depends(get_db)
) -> Any:
    """Verify user email"""
    # Implementation from existing auth module
    pass


@router.post("/forgot-password")
async def forgot_password(
    db: Session = Depends(get_db)
) -> Any:
    """Forgot password"""
    # Implementation from existing auth module
    pass