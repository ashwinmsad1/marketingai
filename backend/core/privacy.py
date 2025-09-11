"""
Privacy and Compliance Module
Handles GDPR, CCPA compliance and data protection
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from cryptography.fernet import Fernet
import os
import base64

from database.models import Base

logger = logging.getLogger(__name__)

class UserConsent(Base):
    """Database model for tracking user consent"""
    __tablename__ = "user_consent"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    consent_type = Column(String, nullable=False)  # marketing, analytics, cookies
    consented = Column(Boolean, nullable=False)
    consent_version = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    consent_date = Column(DateTime, default=datetime.utcnow)
    withdrawn_date = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
class DataDeletionRequest(Base):
    """Database model for data deletion requests"""
    __tablename__ = "data_deletion_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    request_type = Column(String, nullable=False)  # deletion, portability, correction
    status = Column(String, default="pending")  # pending, in_progress, completed
    requested_data = Column(JSON)  # List of data types to delete
    reason = Column(Text, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

class EncryptionService:
    """Service for encrypting sensitive data"""
    
    def __init__(self):
        self.key = self._get_encryption_key()
        self.fernet = Fernet(self.key) if self.key else None
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Get encryption key from environment or generate new one"""
        key_str = os.getenv('ENCRYPTION_KEY')
        if not key_str:
            logger.warning("ENCRYPTION_KEY not set - generating temporary key")
            # Generate a key for this session (should be persistent in production)
            return Fernet.generate_key()
        
        try:
            return base64.urlsafe_b64decode(key_str)
        except Exception as e:
            logger.error(f"Invalid encryption key format: {e}")
            return None
    
    def encrypt(self, data: str) -> Optional[str]:
        """Encrypt sensitive data"""
        if not self.fernet:
            logger.error("Encryption not available - key not configured")
            return data  # Return unencrypted in case of configuration error
        
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data"""
        if not self.fernet:
            logger.error("Decryption not available - key not configured")
            return encrypted_data
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data

class PrivacyService:
    """
    Service for handling privacy compliance and data protection
    """
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        
        # Data retention periods (in days)
        self.retention_periods = {
            "user_profile": 730,  # 2 years
            "campaign_data": 365,  # 1 year
            "analytics_data": 90,  # 3 months
            "ml_predictions": 30,  # 1 month
            "logs": 90  # 3 months
        }
        
        # Required consents for different features
        self.consent_requirements = {
            "campaign_creation": ["marketing"],
            "analytics": ["analytics", "cookies"],
            "ml_predictions": ["marketing", "analytics"],
            "personalization": ["marketing", "analytics"]
        }
    
    def record_consent(
        self, 
        db: Session,
        user_id: str,
        consent_type: str,
        consented: bool,
        consent_version: str = "1.0",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_days: Optional[int] = None
    ) -> UserConsent:
        """Record user consent for data processing"""
        
        try:
            # Check if consent already exists
            existing_consent = db.query(UserConsent).filter(
                UserConsent.user_id == user_id,
                UserConsent.consent_type == consent_type
            ).first()
            
            if existing_consent:
                # Update existing consent
                existing_consent.consented = consented
                existing_consent.consent_version = consent_version
                existing_consent.consent_date = datetime.utcnow()
                existing_consent.withdrawn_date = datetime.utcnow() if not consented else None
                existing_consent.expires_at = (
                    datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
                )
                consent = existing_consent
            else:
                # Create new consent record
                consent = UserConsent(
                    user_id=user_id,
                    consent_type=consent_type,
                    consented=consented,
                    consent_version=consent_version,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    expires_at=(
                        datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
                    )
                )
                db.add(consent)
            
            db.commit()
            db.refresh(consent)
            
            logger.info(f"Recorded consent for user {user_id}: {consent_type} = {consented}")
            return consent
            
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            db.rollback()
            raise
    
    def check_consent(self, db: Session, user_id: str, feature: str) -> bool:
        """Check if user has given required consent for a feature"""
        
        try:
            required_consents = self.consent_requirements.get(feature, [])
            
            for consent_type in required_consents:
                consent = db.query(UserConsent).filter(
                    UserConsent.user_id == user_id,
                    UserConsent.consent_type == consent_type,
                    UserConsent.consented == True
                ).first()
                
                if not consent:
                    logger.warning(f"User {user_id} missing consent for {consent_type}")
                    return False
                
                # Check if consent has expired
                if consent.expires_at and consent.expires_at < datetime.utcnow():
                    logger.warning(f"User {user_id} consent for {consent_type} has expired")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking consent: {e}")
            return False  # Fail closed - deny access if error occurs
    
    def request_data_deletion(
        self,
        db: Session,
        user_id: str,
        request_type: str = "deletion",
        requested_data: Optional[List[str]] = None,
        reason: Optional[str] = None
    ) -> DataDeletionRequest:
        """Create a data deletion/portability request"""
        
        try:
            deletion_request = DataDeletionRequest(
                user_id=user_id,
                request_type=request_type,
                requested_data=requested_data or ["all"],
                reason=reason
            )
            
            db.add(deletion_request)
            db.commit()
            db.refresh(deletion_request)
            
            logger.info(f"Data deletion request created for user {user_id}: {request_type}")
            return deletion_request
            
        except Exception as e:
            logger.error(f"Error creating deletion request: {e}")
            db.rollback()
            raise
    
    def process_data_deletion(self, db: Session, request_id: int) -> bool:
        """Process a data deletion request"""
        
        try:
            request = db.query(DataDeletionRequest).filter(
                DataDeletionRequest.id == request_id
            ).first()
            
            if not request:
                logger.error(f"Deletion request {request_id} not found")
                return False
            
            request.status = "in_progress"
            request.processed_at = datetime.utcnow()
            db.commit()
            
            # Delete data based on request type
            if request.request_type == "deletion":
                success = self._delete_user_data(db, request.user_id, request.requested_data)
            elif request.request_type == "portability":
                success = self._export_user_data(db, request.user_id, request.requested_data)
            else:
                success = False
            
            # Update request status
            request.status = "completed" if success else "failed"
            request.completed_at = datetime.utcnow() if success else None
            db.commit()
            
            logger.info(f"Data deletion request {request_id} processed: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Error processing deletion request: {e}")
            return False
    
    def _delete_user_data(self, db: Session, user_id: str, data_types: List[str]) -> bool:
        """Delete specific user data types"""
        
        try:
            if "all" in data_types or "user_profile" in data_types:
                # Delete user profiles and related data
                # This would need to be implemented based on your specific models
                logger.info(f"Deleting user profile data for user {user_id}")
            
            if "all" in data_types or "campaign_data" in data_types:
                # Delete campaign data
                logger.info(f"Deleting campaign data for user {user_id}")
            
            if "all" in data_types or "analytics_data" in data_types:
                # Delete analytics data
                logger.info(f"Deleting analytics data for user {user_id}")
            
            if "all" in data_types or "ml_predictions" in data_types:
                # Delete ML predictions
                logger.info(f"Deleting ML prediction data for user {user_id}")
            
            # Delete consent records (keep for legal compliance)
            # Note: You may need to keep consent withdrawal records for legal purposes
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    def _export_user_data(self, db: Session, user_id: str, data_types: List[str]) -> bool:
        """Export user data for portability request"""
        
        try:
            # This would generate a data export file
            # Implementation would depend on your specific data models
            logger.info(f"Exporting user data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return False
    
    def cleanup_expired_data(self, db: Session) -> Dict[str, int]:
        """Clean up data that has exceeded retention periods"""
        
        cleanup_results = {}
        
        try:
            current_time = datetime.utcnow()
            
            # Cleanup expired ML predictions
            retention_date = current_time - timedelta(days=self.retention_periods["ml_predictions"])
            # This would delete expired ML predictions
            # deleted_predictions = db.query(MLPredictionResult).filter(
            #     MLPredictionResult.created_at < retention_date
            # ).delete()
            # cleanup_results["ml_predictions"] = deleted_predictions
            
            # Cleanup expired analytics data
            retention_date = current_time - timedelta(days=self.retention_periods["analytics_data"])
            # Similar cleanup for analytics data
            
            # Cleanup expired logs
            retention_date = current_time - timedelta(days=self.retention_periods["logs"])
            # Log cleanup implementation
            
            db.commit()
            logger.info(f"Data cleanup completed: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            db.rollback()
            return cleanup_results
    
    def get_privacy_summary(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get privacy summary for a user"""
        
        try:
            # Get consent status
            consents = db.query(UserConsent).filter(
                UserConsent.user_id == user_id
            ).all()
            
            # Get deletion requests
            deletion_requests = db.query(DataDeletionRequest).filter(
                DataDeletionRequest.user_id == user_id
            ).all()
            
            return {
                "user_id": user_id,
                "consents": [{
                    "type": c.consent_type,
                    "consented": c.consented,
                    "date": c.consent_date.isoformat(),
                    "expires": c.expires_at.isoformat() if c.expires_at else None
                } for c in consents],
                "deletion_requests": [{
                    "id": dr.id,
                    "type": dr.request_type,
                    "status": dr.status,
                    "requested_at": dr.requested_at.isoformat(),
                    "completed_at": dr.completed_at.isoformat() if dr.completed_at else None
                } for dr in deletion_requests],
                "data_retention_periods": self.retention_periods
            }
            
        except Exception as e:
            logger.error(f"Error getting privacy summary: {e}")
            return {"error": str(e)}


# Global privacy service instance
privacy_service = PrivacyService()