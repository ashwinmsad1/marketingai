"""
Pydantic models for authentication
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    """User registration model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    company_name: Optional[str] = Field(None, max_length=100, description="Company name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class PasswordReset(BaseModel):
    """Password reset request model"""
    email: EmailStr = Field(..., description="User email address")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")

class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

class Token(BaseModel):
    """JWT token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token payload data"""
    user_id: str

class RefreshToken(BaseModel):
    """Refresh token request model"""
    refresh_token: str = Field(..., description="Refresh token")

class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    email: str
    first_name: str
    last_name: str
    company_name: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: str
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """User profile update model"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    company_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

class EmailVerification(BaseModel):
    """Email verification model"""
    token: str = Field(..., description="Verification token")

# Response models
class AuthResponse(BaseModel):
    """Authentication response model"""
    user: UserProfile
    tokens: Token
    message: str = "Authentication successful"

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True