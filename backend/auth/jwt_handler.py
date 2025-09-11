"""
JWT token handling for authentication
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..database.models import User
from ..database.crud import UserCRUD
from .models import TokenData
from ..utils.config_manager import get_config

# JWT Configuration using secure config manager
SECRET_KEY = get_config("SECRET_KEY")
ALGORITHM = get_config("JWT_ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_config("ACCESS_TOKEN_EXPIRE_MINUTES") or "30")
REFRESH_TOKEN_EXPIRE_DAYS = int(get_config("REFRESH_TOKEN_EXPIRE_DAYS") or "7")

security = HTTPBearer()

class JWTHandler:
    """Handle JWT token operations"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            token_type_from_payload: str = payload.get("type")
            
            if user_id is None or token_type_from_payload != token_type:
                return None
            
            return TokenData(user_id=user_id)
        except JWTError:
            return None
    
    @staticmethod
    def create_tokens(user_id: str) -> dict:
        """Create both access and refresh tokens"""
        access_token = JWTHandler.create_access_token(data={"sub": user_id})
        refresh_token = JWTHandler.create_refresh_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = JWTHandler.verify_token(token)
        
        if token_data is None:
            raise credentials_exception
            
        user = UserCRUD.get_user(db, user_id=token_data.user_id)
        if user is None:
            raise credentials_exception
            
        return user
    except JWTError:
        raise credentials_exception

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (not disabled)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current verified user (email verified)"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Email verification required",
                "error_code": "EMAIL_NOT_VERIFIED",
                "user_email": current_user.email,
                "requires_verification": True
            }
        )
    return current_user

async def get_current_active_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current active and verified user (combines both checks)"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Email verification required to access this feature",
                "error_code": "EMAIL_NOT_VERIFIED",
                "user_email": current_user.email,
                "requires_verification": True
            }
        )
    return current_user

# Optional authentication (user may or may not be logged in)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        token_data = JWTHandler.verify_token(token)
        
        if token_data is None:
            return None
            
        user = UserCRUD.get_user(db, user_id=token_data.user_id)
        return user
    except:
        return None