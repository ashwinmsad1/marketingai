"""
Privacy and Compliance API endpoints
Handles GDPR, CCPA requests and consent management
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field

from backend.app.dependencies import get_db, get_current_verified_user
from backend.database.models import User
from backend.core.privacy import privacy_service

logger = logging.getLogger(__name__)
router = APIRouter()

class ConsentRequest(BaseModel):
    """Request model for consent recording"""
    consent_type: str = Field(..., description="Type of consent (marketing, analytics, cookies)")
    consented: bool = Field(..., description="Whether user consented")
    consent_version: str = Field(default="1.0", description="Version of consent terms")

class DataDeletionRequest(BaseModel):
    """Request model for data deletion"""
    request_type: str = Field(default="deletion", description="Type of request (deletion, portability)")
    requested_data: List[str] = Field(default=["all"], description="Data types to delete")
    reason: Optional[str] = Field(None, description="Reason for deletion request")

@router.post("/consent")
async def record_user_consent(
    request: Request,
    consent_request: ConsentRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Record user consent for data processing
    
    This endpoint is required for GDPR compliance to track explicit consent
    for different types of data processing.
    """
    try:
        # Extract client information for consent record
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Record consent
        consent = privacy_service.record_consent(
            db=db,
            user_id=str(current_user.id),
            consent_type=consent_request.consent_type,
            consented=consent_request.consented,
            consent_version=consent_request.consent_version,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        logger.info(f"Recorded consent for user {current_user.id}: {consent_request.consent_type} = {consent_request.consented}")
        
        return {
            "status": "success",
            "message": f"Consent recorded for {consent_request.consent_type}",
            "consent_id": consent.id,
            "recorded_at": consent.consent_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error recording consent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record consent"
        )

@router.get("/consent/status")
async def get_consent_status(
    feature: Optional[str] = None,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get user's consent status for features
    
    Returns current consent status and whether user can access specific features
    based on their consent choices.
    """
    try:
        if feature:
            # Check consent for specific feature
            has_consent = privacy_service.check_consent(
                db=db,
                user_id=str(current_user.id),
                feature=feature
            )
            
            return {
                "user_id": str(current_user.id),
                "feature": feature,
                "has_consent": has_consent,
                "message": "Feature access allowed" if has_consent else "Additional consent required"
            }
        else:
            # Get comprehensive privacy summary
            privacy_summary = privacy_service.get_privacy_summary(
                db=db,
                user_id=str(current_user.id)
            )
            
            return {
                "status": "success",
                "privacy_summary": privacy_summary
            }
            
    except Exception as e:
        logger.error(f"Error getting consent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consent status"
        )

@router.post("/data-deletion")
async def request_data_deletion(
    deletion_request: DataDeletionRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Request data deletion or portability (GDPR Article 17, 20)
    
    Allows users to request deletion of their personal data or export
    for portability to another service.
    """
    try:
        # Create deletion request
        request_record = privacy_service.request_data_deletion(
            db=db,
            user_id=str(current_user.id),
            request_type=deletion_request.request_type,
            requested_data=deletion_request.requested_data,
            reason=deletion_request.reason
        )
        
        logger.info(f"Data deletion request created for user {current_user.id}: {deletion_request.request_type}")
        
        return {
            "status": "success",
            "message": f"Data {deletion_request.request_type} request submitted",
            "request_id": request_record.id,
            "estimated_completion": "7-30 days",
            "next_steps": [
                "Your request has been logged and will be processed",
                "You will receive confirmation once processing is complete",
                "Contact support if you have questions about this request"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error creating data deletion request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create deletion request"
        )

@router.get("/data-requests")
async def get_data_requests(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get user's data deletion and portability requests
    
    Shows the status of all privacy-related requests made by the user.
    """
    try:
        from backend.core.privacy import DataDeletionRequest
        
        requests = db.query(DataDeletionRequest).filter(
            DataDeletionRequest.user_id == str(current_user.id)
        ).order_by(DataDeletionRequest.requested_at.desc()).all()
        
        return {
            "status": "success",
            "requests": [{
                "id": req.id,
                "type": req.request_type,
                "status": req.status,
                "requested_data": req.requested_data,
                "requested_at": req.requested_at.isoformat(),
                "processed_at": req.processed_at.isoformat() if req.processed_at else None,
                "completed_at": req.completed_at.isoformat() if req.completed_at else None
            } for req in requests]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving data requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve data requests"
        )

@router.get("/privacy-policy")
async def get_privacy_policy():
    """
    Get current privacy policy and consent requirements
    
    Returns the privacy policy text and required consents for different features.
    """
    return {
        "privacy_policy": {
            "version": "1.0",
            "last_updated": "2024-01-01",
            "summary": "We process your data to provide marketing automation services",
            "data_types_collected": [
                "Profile information (name, email, company)",
                "Campaign performance data",
                "Usage analytics and preferences",
                "Marketing automation settings"
            ],
            "data_usage": [
                "Providing personalized marketing recommendations",
                "Analyzing campaign performance and optimization",
                "Improving our AI/ML models and services",
                "Communicating about your account and services"
            ],
            "data_sharing": [
                "Facebook/Instagram APIs for campaign management",
                "Analytics providers for performance tracking",
                "No data sold to third parties"
            ],
            "user_rights": [
                "Access your personal data",
                "Request correction of inaccurate data",
                "Request deletion of your data",
                "Data portability to other services",
                "Withdraw consent at any time"
            ]
        },
        "consent_requirements": {
            "marketing": {
                "required_for": ["campaign_creation", "personalization", "ml_predictions"],
                "description": "Process your data for marketing automation and recommendations"
            },
            "analytics": {
                "required_for": ["performance_tracking", "usage_analytics", "ml_predictions"],
                "description": "Analyze usage patterns and campaign performance"
            },
            "cookies": {
                "required_for": ["session_management", "preferences", "analytics"],
                "description": "Store preferences and maintain your session"
            }
        },
        "contact": {
            "data_protection_officer": "privacy@marketingai.com",
            "support": "support@marketingai.com"
        }
    }

@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Complete account deletion
    
    WARNING: This will permanently delete the user's account and all associated data.
    This action cannot be undone.
    """
    try:
        # Create deletion request for all data
        deletion_request = privacy_service.request_data_deletion(
            db=db,
            user_id=str(current_user.id),
            request_type="deletion",
            requested_data=["all"],
            reason="Complete account deletion"
        )
        
        # Process the deletion immediately for account deletion
        success = privacy_service.process_data_deletion(db, deletion_request.id)
        
        if success:
            logger.info(f"Account deleted for user {current_user.id}")
            return {
                "status": "success",
                "message": "Account and all associated data have been permanently deleted",
                "deletion_completed_at": deletion_request.completed_at.isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account deletion failed - please contact support"
            )
            
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

# Middleware for consent checking
async def check_feature_consent(feature: str, user_id: str, db: Session) -> bool:
    """
    Middleware function to check consent before feature access
    
    This should be used as a dependency in other API endpoints that require
    specific consent types.
    """
    return privacy_service.check_consent(db=db, user_id=user_id, feature=feature)

@router.get("/compliance-status")
async def get_compliance_status():
    """
    Get platform compliance status and certifications
    
    Shows current compliance status with various privacy regulations.
    """
    return {
        "compliance": {
            "gdpr": {
                "compliant": True,
                "features": [
                    "Explicit consent collection and tracking",
                    "Right to access personal data",
                    "Right to rectification",
                    "Right to erasure (right to be forgotten)",
                    "Right to data portability",
                    "Right to object to processing"
                ],
                "lawful_basis": "Consent and legitimate interest"
            },
            "ccpa": {
                "compliant": True,
                "features": [
                    "Consumer right to know",
                    "Consumer right to delete",
                    "Consumer right to opt-out",
                    "Non-discrimination for exercising rights"
                ]
            },
            "platform_terms": {
                "facebook": {
                    "compliant": True,
                    "features": [
                        "User consent before API access",
                        "Proper data handling and storage",
                        "Respect for user privacy settings"
                    ]
                },
                "instagram": {
                    "compliant": True,
                    "features": [
                        "User consent before API access",
                        "Proper data handling and storage",
                        "Respect for user privacy settings"
                    ]
                }
            }
        },
        "certifications": [
            "SOC 2 Type II (in progress)",
            "ISO 27001 (in progress)"
        ],
        "data_protection": {
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "access_controls": True,
            "audit_logging": True,
            "data_retention_policies": True
        }
    }