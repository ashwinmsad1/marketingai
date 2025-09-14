"""
Authentication package for AI Marketing Automation Platform
"""
from .jwt_handler import JWTHandler, get_current_user, get_current_active_user
from .password import PasswordHandler
from .models import (
    UserRegister, UserLogin, Token, TokenData, UserProfile, 
    AuthResponse, MessageResponse, UserUpdate
)

# Create convenience functions for the API routes
def authenticate_user(db, email: str, password: str):
    """Authenticate user with email and password"""
    # TODO: Implement actual authentication logic
    return None

def create_tokens(user_id: str):
    """Create JWT tokens for user"""
    jwt_handler = JWTHandler()
    return jwt_handler.create_tokens(user_id)