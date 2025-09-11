"""
User Service Layer
Handles user-related business logic
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from database.crud import UserCRUD, SubscriptionCRUD

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user management"""
    
    def __init__(self):
        """Initialize user service"""
        pass
    
    def get_user_profile(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get user profile with subscription information
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User profile data
        """
        try:
            user = UserCRUD.get_user(db, user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Get active subscription
            subscription = SubscriptionCRUD.get_active_subscription(db, user_id)
            subscription_tier = subscription.tier.value if subscription else "starter"
            
            profile_data = {
                "id": user.id,
                "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or "Unknown User",
                "email": user.email,
                "subscription_tier": subscription_tier,
                "industry": "General",  # Could be stored in user profile
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
            
            logger.info(f"Retrieved profile for user {user_id}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise
    
    def update_user_profile(
        self, 
        db: Session, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user profile information
        
        Args:
            db: Database session
            user_id: User ID
            update_data: Fields to update
            
        Returns:
            Updated user profile
        """
        try:
            # Update user
            user = UserCRUD.update_user(db, user_id, **update_data)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Return updated profile
            return self.get_user_profile(db, user_id)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise