"""
Authentication package for AI Marketing Automation Platform
"""
from .jwt_handler import JWTHandler, get_current_user, get_current_active_user
from .password import PasswordHandler
from .models import UserRegister, UserLogin, Token, TokenData