"""
Authentication package for AI Marketing Automation Platform
"""
from auth.jwt_handler import JWTHandler, get_current_user, get_current_active_user
from auth.password import PasswordHandler
from auth.models import UserRegister, UserLogin, Token, TokenData