"""
Authentication API routes for FastAPI
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from database.models import User, SubscriptionTier
from database.crud import UserCRUD, SubscriptionCRUD
from datetime import datetime
from auth.models import (
    UserRegister, UserLogin, Token, AuthResponse, MessageResponse,
    PasswordReset, PasswordResetConfirm, PasswordChange, UserProfile,
    UserUpdate, EmailVerification
)
from pydantic import BaseModel
from auth.jwt_handler import JWTHandler, get_current_user, get_current_active_user
from auth.password import PasswordHandler
from auth.email_handler import EmailHandler
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = UserCRUD.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Validate password strength
    is_strong, issues = PasswordHandler.is_password_strong(user_data.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet security requirements", "issues": issues}
        )
    
    try:
        # Hash password
        hashed_password = PasswordHandler.hash_password(user_data.password)
        
        # Create user
        user = UserCRUD.create_user(
            db=db,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            company_name=user_data.company_name,
            phone=user_data.phone,
            is_verified=False  # Email verification required
        )
        
        # Create default starter subscription (Essential plan)
        subscription = SubscriptionCRUD.create_subscription(
            db=db,
            user_id=user.id,
            tier=SubscriptionTier.STARTER,
            monthly_price=599.00,  # Essential Plan pricing
            max_campaigns=10,
            max_ai_generations=-1,  # Unlimited basic AI content
            is_trial=True
        )
        
        # Generate email verification token
        verification_token = EmailHandler.generate_verification_token(user.id)
        
        # Send verification email in background
        background_tasks.add_task(
            EmailHandler.send_verification_email, 
            user, 
            verification_token
        )
        
        # Generate JWT tokens
        tokens = JWTHandler.create_tokens(user.id)
        
        # Prepare response with compatibility
        user_dict = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company_name": user.company_name,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat()
        }
        
        # Add computed name field for frontend compatibility
        if user.first_name and user.last_name:
            user_dict["name"] = f"{user.first_name} {user.last_name}".strip()
        
        user_profile = UserProfile(**user_dict)
        
        logger.info(f"New user registered: {user.email}")
        
        return AuthResponse(
            user=user_profile,
            tokens=Token(**tokens),
            message="Registration successful! Please check your email to verify your account."
        )
        
    except Exception as e:
        logger.error(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    # Get user by email
    user = UserCRUD.get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not PasswordHandler.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Please contact support."
        )
    
    # Update last login
    UserCRUD.update_user(db, user.id, last_login=datetime.now())
    
    # Generate JWT tokens
    tokens = JWTHandler.create_tokens(user.id)
    
    # Prepare response with compatibility
    user_dict = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "company_name": user.company_name,
        "phone": user.phone,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat()
    }
    
    # Add computed name field for frontend compatibility
    if user.first_name and user.last_name:
        user_dict["name"] = f"{user.first_name} {user.last_name}".strip()
    
    user_profile = UserProfile(**user_dict)
    
    logger.info(f"User logged in: {user.email}")
    
    return AuthResponse(
        user=user_profile,
        tokens=Token(**tokens),
        message="Login successful!"
    )

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh JWT access token"""
    # Verify refresh token
    token_data = JWTHandler.verify_token(request.refresh_token, token_type="refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if user exists
    user = UserCRUD.get_user(db, token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    tokens = JWTHandler.create_tokens(user.id)
    
    return Token(**tokens)

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    # Prepare response with compatibility
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "company_name": current_user.company_name,
        "phone": current_user.phone,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat()
    }
    
    # Add computed name field for frontend compatibility
    if current_user.first_name and current_user.last_name:
        user_dict["name"] = f"{current_user.first_name} {current_user.last_name}".strip()
    
    return UserProfile(**user_dict)

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    # Prepare update data (only include non-None values)
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    # Update user
    updated_user = UserCRUD.update_user(db, current_user.id, **update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile(
        id=updated_user.id,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        company_name=updated_user.company_name,
        phone=updated_user.phone,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        created_at=updated_user.created_at.isoformat()
    )

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify user email address"""
    # Verify token
    user_id = EmailHandler.verify_email_token(verification.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Update user verification status
    user = UserCRUD.update_user(db, user_id, is_verified=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"Email verified for user: {user.email}")
    
    return MessageResponse(
        message="Email verified successfully! You can now access all platform features.",
        success=True
    )

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resend email verification to current user"""
    # Check if user is already verified
    if current_user.is_verified:
        return MessageResponse(
            message="Your email is already verified!",
            success=True
        )
    
    try:
        # Generate new verification token
        verification_token = EmailHandler.generate_verification_token(current_user.id)
        
        # Send verification email in background
        background_tasks.add_task(
            EmailHandler.send_verification_email, 
            current_user, 
            verification_token
        )
        
        logger.info(f"Verification email resent to: {current_user.email}")
        
        return MessageResponse(
            message="Verification email sent! Please check your inbox and spam folder.",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Failed to resend verification email to {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again."
        )

@router.get("/verification-status", response_model=dict)
async def get_verification_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's email verification status"""
    return {
        "is_verified": current_user.is_verified,
        "email": current_user.email,
        "user_id": current_user.id,
        "requires_verification": not current_user.is_verified
    }

@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    reset_request: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    # Check if user exists
    user = UserCRUD.get_user_by_email(db, reset_request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return MessageResponse(
            message="If an account with this email exists, you will receive a password reset link.",
            success=True
        )
    
    # Generate reset token
    reset_token = EmailHandler.generate_reset_token(user.id)
    
    # Send reset email in background
    background_tasks.add_task(
        EmailHandler.send_reset_email,
        user,
        reset_token
    )
    
    logger.info(f"Password reset requested for: {user.email}")
    
    return MessageResponse(
        message="If an account with this email exists, you will receive a password reset link.",
        success=True
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset user password"""
    # Verify reset token
    user_id = EmailHandler.verify_reset_token(reset_data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    is_strong, issues = PasswordHandler.is_password_strong(reset_data.new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet security requirements", "issues": issues}
        )
    
    # Hash new password
    hashed_password = PasswordHandler.hash_password(reset_data.new_password)
    
    # Update user password
    user = UserCRUD.update_user(db, user_id, password_hash=hashed_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"Password reset completed for user: {user.email}")
    
    return MessageResponse(
        message="Password reset successful! You can now login with your new password.",
        success=True
    )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password (requires current password)"""
    # Verify current password
    if not PasswordHandler.verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    is_strong, issues = PasswordHandler.is_password_strong(password_change.new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet security requirements", "issues": issues}
        )
    
    # Check if new password is different from current
    if PasswordHandler.verify_password(password_change.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Hash new password
    hashed_password = PasswordHandler.hash_password(password_change.new_password)
    
    # Update user password
    UserCRUD.update_user(db, current_user.id, password_hash=hashed_password)
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return MessageResponse(
        message="Password changed successfully!",
        success=True
    )

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """Logout user (client should delete tokens)"""
    logger.info(f"User logged out: {current_user.email}")
    
    return MessageResponse(
        message="Logged out successfully!",
        success=True
    )