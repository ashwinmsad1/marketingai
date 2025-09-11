"""
Campaign management API endpoints with budget safety controls and tier enforcement
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Any
import logging

from backend.app.dependencies import get_db, get_current_verified_user
from backend.database.models import User, Campaign
from backend.services import CampaignService
from backend.services.budget_service import BudgetService
from backend.services.usage_tracking_service import UsageTrackingService
from backend.engines.marketing_automation import EnhancedMarketingAutomationEngine
from backend.core.schemas import CampaignCreateRequest, CampaignResponse, ErrorResponse
from backend.core.config import settings
from backend.core.exceptions import (
    BudgetValidationError, 
    budget_exceeded_exception,
    insufficient_funds_exception,
    validation_exception
)
from backend.core.tier_enforcement import (
    campaign_creation_guard,
    TierEnforcementError,
    require_tier,
    feature_usage_guard
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
campaign_service = CampaignService()
marketing_engine = EnhancedMarketingAutomationEngine()


@router.post("/create", response_model=CampaignResponse)
@campaign_creation_guard
async def create_campaign(
    request: CampaignCreateRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    http_request: Request = None
) -> CampaignResponse:
    """
    Create new marketing campaign with comprehensive budget validation and tier enforcement
    
    This endpoint implements critical safety controls to prevent budget overspend:
    - Validates budget against subscription tier limits
    - Checks monthly spending caps
    - Validates user balance
    - Enforces campaign count limits
    - Enforces tier-based campaign creation limits
    """
    try:
        # Set user context for tier enforcement middleware
        if http_request:
            http_request.state.user_id = str(current_user.id)
            http_request.state.user_tier = getattr(current_user, 'subscription_tier', 'basic')
        # Initialize budget service
        budget_service = BudgetService(db)
        
        # Step 1: Comprehensive budget validation
        logger.info(f"Validating budget for user {current_user.id}, budget: {request.budget}")
        
        try:
            budget_validation = budget_service.validate_campaign_budget(
                user=current_user,
                budget=request.budget
            )
        except BudgetValidationError as e:
            logger.warning(f"Budget validation failed for user {current_user.id}: {str(e)}")
            raise budget_exceeded_exception(detail=str(e))
        
        # Step 2: Check validation results
        if not budget_validation.is_valid:
            error_details = "; ".join(budget_validation.errors)
            logger.warning(f"Budget validation failed for user {current_user.id}: {error_details}")
            
            # Return specific error based on error type
            if "insufficient" in error_details.lower() or "balance" in error_details.lower():
                raise insufficient_funds_exception(detail=error_details)
            else:
                raise budget_exceeded_exception(detail=error_details)
        
        # Step 3: Log warnings if any
        if budget_validation.warnings:
            warning_details = "; ".join(budget_validation.warnings)
            logger.info(f"Budget validation warnings for user {current_user.id}: {warning_details}")
        
        # Step 4: Prepare campaign data for engine
        campaign_data = {
            "user_id": current_user.id,
            "name": request.name,
            "description": request.description,
            "type": request.type.value,
            "prompt": request.prompt,
            "caption": request.caption,
            "style": request.style,
            "aspectRatio": request.aspect_ratio,
            "platforms": {
                "facebook": request.platforms.facebook,
                "instagram": request.platforms.instagram
            },
            "budget": {
                "daily_budget": request.budget.daily_budget,
                "total_budget": request.budget.total_budget,
                "duration_days": request.budget.duration_days
            },
            "targeting": request.targeting.dict() if request.targeting else {},
            "auto_optimization": request.auto_optimization,
            "schedule_start": request.schedule_start,
            "schedule_end": request.schedule_end
        }
        
        # Step 5: Route to appropriate engine based on campaign type
        logger.info(f"Creating {request.type.value} campaign for user {current_user.id}")
        
        if request.type == "video":
            result = await marketing_engine.create_and_post_video_campaign(
                prompt=request.prompt,
                caption=request.caption or "",
                user_id=str(current_user.id),
                style=request.style or "cinematic",
                aspect_ratio=request.aspect_ratio or "16:9"
            )
        elif request.type == "viral":
            result = await marketing_engine.create_viral_trend_campaign(
                user_id=str(current_user.id)
            )
        else:
            # Default image campaign
            result = await marketing_engine.create_and_post_image_campaign(
                prompt=request.prompt,
                caption=request.caption or "",
                user_id=str(current_user.id)
            )
        
        # Step 6: Return success response with budget validation info
        logger.info(f"Successfully created campaign for user {current_user.id}")
        
        return CampaignResponse(
            success=True,
            message="Campaign created successfully",
            data=result,
            budget_validation=budget_validation,
            warnings=budget_validation.warnings
        )
        
    except TierEnforcementError as e:
        # Handle tier limit violations with detailed upgrade information
        logger.warning(f"Tier limit exceeded for user {current_user.id}: {e.detail}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "tier_limit_exceeded",
                "message": e.detail,
                "current_tier": e.current_tier,
                "suggested_tier": e.suggested_tier,
                "usage_info": e.usage_info,
                "upgrade_url": f"/subscription/upgrade/{e.suggested_tier}" if e.suggested_tier else None
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (budget errors, validation errors)
        raise
        
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error creating campaign for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the campaign. Please try again."
        )


@router.get("/")
async def get_campaigns(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's campaigns"""
    campaigns = campaign_service.get_user_campaigns(db, current_user.id)
    return {"success": True, "data": campaigns}


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific campaign"""
    campaign = campaign_service.get_campaign(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return {"success": True, "data": campaign}


@router.put("/{campaign_id}")
async def update_campaign(
    campaign_id: int,
    campaign_data: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update campaign"""
    campaign = campaign_service.update_campaign(
        db, campaign_id, campaign_data, current_user.id
    )
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return {"success": True, "data": campaign}


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete campaign"""
    success = campaign_service.delete_campaign(db, campaign_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return {"success": True, "message": "Campaign deleted successfully"}


@router.get("/usage-status")
async def get_usage_status(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user's current usage status across all tier metrics
    
    Provides transparency about:
    - Campaign creation usage vs limits
    - AI generation usage vs limits  
    - Ad spend monitoring usage vs limits
    - Current tier and upgrade suggestions
    """
    try:
        # Get current subscription tier
        user_tier = getattr(current_user, 'subscription_tier', 'basic')
        
        # Get usage summary from tracking service
        usage_summary = UsageTrackingService.get_usage_summary(db, str(current_user.id))
        
        # Get tier limits for comparison
        from backend.utils.usage_helpers import UsageHelpers
        tier_limits = UsageHelpers.get_tier_limits(user_tier)
        
        # Calculate usage percentages
        usage_percentages = {}
        for metric in ['campaigns', 'ai_generations', 'ad_spend']:
            current_usage = usage_summary["usage"][metric]
            limit = tier_limits[metric]
            usage_percentages[metric] = UsageHelpers.calculate_usage_percentage(current_usage, limit)
        
        # Generate warnings if needed
        warnings = UsageHelpers.generate_usage_warnings(usage_percentages)
        
        # Get upgrade suggestions
        upgrade_tier = UsageHelpers.get_tier_upgrade_path(user_tier)
        
        return {
            "success": True,
            "data": {
                "current_tier": user_tier,
                "usage_summary": usage_summary,
                "tier_limits": tier_limits,
                "usage_percentages": usage_percentages,
                "warnings": warnings,
                "upgrade_available": upgrade_tier is not None,
                "suggested_tier": upgrade_tier,
                "days_until_reset": UsageHelpers.get_days_until_reset(),
                "next_reset_date": UsageHelpers.get_next_reset_date().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting usage status for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage status"
        )


@router.get("/budget-status")
async def get_budget_status(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user's current budget status and spending limits
    
    Provides transparency about:
    - Current subscription tier limits
    - Monthly spending vs limits
    - Remaining budget
    - Campaign count vs limits
    """
    try:
        budget_service = BudgetService(db)
        
        # Get subscription info
        subscription = budget_service._get_active_subscription(current_user.id)
        tier = subscription.tier.value if subscription else "starter"
        
        # Get budget limits
        budget_limits = settings.get_budget_limits(tier)
        
        # Get spending summary
        spending_summary = budget_service.get_spending_summary(current_user.id)
        
        # Get campaign count
        campaigns_this_month = budget_service._get_current_month_campaigns(current_user.id)
        
        return {
            "success": True,
            "data": {
                "subscription_tier": tier,
                "budget_limits": budget_limits,
                "spending_summary": spending_summary,
                "campaigns_this_month": campaigns_this_month,
                "remaining_budget": spending_summary["available_balance"] if budget_limits["requires_balance_check"] else budget_limits["monthly_limit"] - spending_summary["current_month_budget"],
                "can_create_campaign": campaigns_this_month < budget_limits.get("max_campaigns_per_month", float('inf'))
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting budget status for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve budget status"
        )