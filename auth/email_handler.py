"""
Email verification and password reset handling
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from database.models import User
from database.crud import UserCRUD
from sqlalchemy.orm import Session

# Email configuration
EMAIL_SECRET_KEY = os.getenv("EMAIL_SECRET_KEY", "email-secret-key-change-in-production")
VERIFICATION_TOKEN_EXPIRE_HOURS = int(os.getenv("VERIFICATION_TOKEN_EXPIRE_HOURS", "24"))
RESET_TOKEN_EXPIRE_HOURS = int(os.getenv("RESET_TOKEN_EXPIRE_HOURS", "1"))

class EmailHandler:
    """Handle email verification and password reset tokens"""
    
    @staticmethod
    def generate_verification_token(user_id: str) -> str:
        """Generate email verification token"""
        expire = datetime.now(timezone.utc) + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "email_verification"
        }
        return jwt.encode(to_encode, EMAIL_SECRET_KEY, algorithm="HS256")
    
    @staticmethod
    def generate_reset_token(user_id: str) -> str:
        """Generate password reset token"""
        expire = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "password_reset",
            "nonce": secrets.token_hex(16)  # Add randomness
        }
        return jwt.encode(to_encode, EMAIL_SECRET_KEY, algorithm="HS256")
    
    @staticmethod
    def verify_email_token(token: str) -> Optional[str]:
        """Verify email verification token and return user_id"""
        try:
            payload = jwt.decode(token, EMAIL_SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if user_id is None or token_type != "email_verification":
                return None
                
            return user_id
        except jwt.JWTError:
            return None
    
    @staticmethod
    def verify_reset_token(token: str) -> Optional[str]:
        """Verify password reset token and return user_id"""
        try:
            payload = jwt.decode(token, EMAIL_SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if user_id is None or token_type != "password_reset":
                return None
                
            return user_id
        except jwt.JWTError:
            return None
    
    @staticmethod
    def send_verification_email(user: User, token: str) -> bool:
        """
        Send verification email to user
        In production, integrate with email service like SendGrid
        """
        # For development, just log the verification link
        verification_link = f"http://localhost:3000/verify-email?token={token}"
        
        print(f"""
        📧 EMAIL VERIFICATION
        To: {user.email}
        Subject: Verify your AI Marketing Platform account
        
        Hi {user.first_name},
        
        Please verify your email address by clicking the link below:
        {verification_link}
        
        This link will expire in {VERIFICATION_TOKEN_EXPIRE_HOURS} hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        AI Marketing Platform Team
        """)
        
        # TODO: Integrate with actual email service
        # Example with SendGrid:
        # import sendgrid
        # from sendgrid.helpers.mail import Mail
        # 
        # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        # message = Mail(
        #     from_email='noreply@aimarketing.com',
        #     to_emails=user.email,
        #     subject='Verify your account',
        #     html_content=html_template
        # )
        # response = sg.send(message)
        
        return True
    
    @staticmethod
    def send_reset_email(user: User, token: str) -> bool:
        """
        Send password reset email to user
        In production, integrate with email service
        """
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        
        print(f"""
        📧 PASSWORD RESET
        To: {user.email}
        Subject: Reset your AI Marketing Platform password
        
        Hi {user.first_name},
        
        We received a request to reset your password. Click the link below to set a new password:
        {reset_link}
        
        This link will expire in {RESET_TOKEN_EXPIRE_HOURS} hour(s).
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        AI Marketing Platform Team
        """)
        
        return True
    
    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """Send welcome email to new user"""
        print(f"""
        📧 WELCOME EMAIL
        To: {user.email}
        Subject: Welcome to AI Marketing Platform!
        
        Hi {user.first_name},
        
        Welcome to AI Marketing Platform! 🎉
        
        Your account has been successfully created. You can now:
        ✅ Create stunning AI-generated images and videos
        ✅ Launch automated marketing campaigns
        ✅ Track performance with detailed analytics
        ✅ Connect your Facebook and Instagram accounts
        
        Get started: http://localhost:3000/dashboard
        
        Need help? Check out our documentation or contact support.
        
        Best regards,
        AI Marketing Platform Team
        """)
        
        return True