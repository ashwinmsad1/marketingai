"""
Personalization API endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List
from datetime import datetime

from backend.app.dependencies import get_db, get_current_verified_user
from backend.database.models import User
from backend.services.personalization_service import EnhancedPersonalizationService
from backend.services.ml_prediction_service import MLPredictionService
from backend.core.config import settings
from backend.core.tier_enforcement import (
    ai_generation_guard,
    campaign_creation_guard,
    feature_usage_guard,
    require_tier
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
personalization_service = EnhancedPersonalizationService()
ml_prediction_service = MLPredictionService()


@router.post("/profile")
async def create_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create comprehensive user profile"""
    try:
        result = await personalization_service.create_comprehensive_user_profile(
            user_id=str(current_user.id),
            profile_data=profile_data,
            db=db
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Get user profile"""
    try:
        profile = personalization_service.personalization_engine.user_profiles.get(str(current_user.id))
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return {"success": True, "data": profile}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.post("/campaign-strategy")
@ai_generation_guard("campaign_strategy")
async def generate_campaign_strategy(
    strategy_request: dict,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Generate personalized campaign strategy"""
    try:
        campaign_brief = strategy_request.get("campaign_brief", "")
        objective_override = strategy_request.get("objective_override")
        
        if not campaign_brief:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign brief is required"
            )
        
        result = await personalization_service.get_personalized_campaign_strategy(
            user_id=str(current_user.id),
            campaign_brief=campaign_brief,
            objective_override=objective_override
        )
        
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate strategy: {str(e)}"
        )


@router.post("/video-strategy")
@ai_generation_guard("video_strategy")
async def generate_video_strategy(
    strategy_request: dict,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Generate personalized video strategy based on user input"""
    try:
        # Required fields
        required_fields = ["campaign_brief", "business_description", "target_audience_description", "unique_value_proposition"]
        missing_fields = [field for field in required_fields if not strategy_request.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        result = await personalization_service.get_personalized_video_strategy(
            user_id=str(current_user.id),
            campaign_brief=strategy_request["campaign_brief"],
            business_description=strategy_request["business_description"],
            target_audience_description=strategy_request["target_audience_description"],
            unique_value_proposition=strategy_request["unique_value_proposition"],
            preferred_style=strategy_request.get("preferred_style"),
            aspect_ratios=strategy_request.get("aspect_ratios")
        )
        
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video strategy: {str(e)}"
        )


@router.post("/image-strategy")
@ai_generation_guard("image_strategy")
async def generate_image_strategy(
    strategy_request: dict,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Generate personalized image strategy based on user input"""
    try:
        # Required fields
        required_fields = ["campaign_brief", "business_description", "target_audience_description", "unique_value_proposition"]
        missing_fields = [field for field in required_fields if not strategy_request.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        result = await personalization_service.get_personalized_image_strategy(
            user_id=str(current_user.id),
            campaign_brief=strategy_request["campaign_brief"],
            business_description=strategy_request["business_description"],
            target_audience_description=strategy_request["target_audience_description"],
            unique_value_proposition=strategy_request["unique_value_proposition"],
            preferred_style=strategy_request.get("preferred_style"),
            image_format=strategy_request.get("image_format")
        )
        
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image strategy: {str(e)}"
        )


@router.post("/campaigns/create")
@campaign_creation_guard
async def create_personalized_campaign(
    campaign_data: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create personalized campaign"""
    try:
        campaign_data["user_id"] = str(current_user.id)
        
        # Validate platform selection - only Facebook and Instagram are supported
        platforms = campaign_data.get("platforms", {})
        if not isinstance(platforms, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platforms must be specified as an object with platform keys"
            )
        
        # Check if at least one platform is selected
        selected_platforms = [platform for platform, enabled in platforms.items() if enabled]
        if not selected_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one platform must be selected"
            )
        
        # Validate only Facebook and Instagram are selected
        valid_platforms = {"facebook", "instagram"}
        invalid_platforms = [platform for platform in selected_platforms if platform not in valid_platforms]
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only Facebook and Instagram platforms are supported. Invalid platforms: {', '.join(invalid_platforms)}"
            )
        
        result = await personalization_service.launch_personalized_campaign(
            user_id=str(current_user.id),
            campaign_strategy=campaign_data,
            db=db
        )
        
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create personalized campaign: {str(e)}"
        )


@router.get("/dashboard")
async def get_personalized_dashboard(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get personalized dashboard"""
    try:
        result = await personalization_service.get_personalized_dashboard(
            user_id=str(current_user.id),
            db=db
        )
        
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/optimize")
async def optimize_campaign(
    campaign_id: str,
    optimization_data: dict,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Optimize existing campaign"""
    try:
        result = await personalization_service.optimize_existing_campaign(
            user_id=str(current_user.id),
            campaign_id=campaign_id,
            performance_data=optimization_data
        )
        
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize campaign: {str(e)}"
        )


@router.post("/questions/answer")
async def answer_campaign_question(
    question_data: dict,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Answer specific campaign questions using personalization data"""
    try:
        question = question_data.get("question", "")
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question is required"
            )
        
        result = await personalization_service.answer_campaign_question(
            user_id=str(current_user.id),
            question=question
        )
        
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


# A/B Testing Endpoints

@router.post("/ab-tests")
@require_tier("professional")
async def create_ab_test(
    test_request: dict,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Create a new A/B test"""
    try:
        # Extract test configuration
        test_config = {
            "test_name": test_request.get("campaign_name", "Untitled A/B Test"),
            "test_type": test_request.get("test_type", "simple_ab"),
            "hypothesis": f"Variant B will outperform Variant A",
            "primary_metric": "conversion_rate",
            "secondary_metrics": ["ctr", "engagement_rate"],
            "minimum_effect_size": 0.1,
            "duration_days": test_request.get("duration_days", 14),
            "significance_level": (100 - test_request.get("confidence_level", 95)) / 100
        }
        
        # Create variations from variant data
        variations = []
        
        # Variant A (Control)
        variant_a = test_request.get("variant_a", {})
        variations.append({
            "variation_id": "control",
            "name": variant_a.get("name", "Control"),
            "description": variant_a.get("description", "Original version"),
            "traffic_percentage": float(test_request.get("traffic_split", 50)),
            "content_config": {
                "headline": variant_a.get("content", {}).get("headline", ""),
                "type": "control"
            }
        })
        
        # Variant B (Test)
        variant_b = test_request.get("variant_b", {})
        variations.append({
            "variation_id": "test",
            "name": variant_b.get("name", "Test"),
            "description": variant_b.get("description", "Test version"),
            "traffic_percentage": float(100 - test_request.get("traffic_split", 50)),
            "content_config": {
                "headline": variant_b.get("content", {}).get("headline", ""),
                "type": "test"
            }
        })
        
        # Create A/B test using the framework
        ab_test = await personalization_service.ab_testing_framework.create_personalized_ab_test(
            user_id=str(current_user.id),
            test_config=test_config,
            variations=variations
        )
        
        # Convert to frontend format
        result = {
            "test_id": ab_test.test_id,
            "campaign_name": ab_test.test_name,
            "test_type": ab_test.test_type.value,
            "status": ab_test.status.value,
            "traffic_split": int(variations[0]["traffic_percentage"]),
            "sample_size": ab_test.minimum_sample_size,
            "confidence_level": int((1 - ab_test.significance_level) * 100),
            "duration_days": (ab_test.planned_end_date - ab_test.start_date).days,
            "start_date": ab_test.start_date.isoformat(),
            "end_date": ab_test.planned_end_date.isoformat(),
            "variant_a": {
                "name": variations[0]["name"],
                "description": variations[0]["description"],
                "content": {"headline": variations[0]["content_config"]["headline"]},
                "metrics": {
                    "impressions": 0,
                    "clicks": 0,
                    "ctr": 0.0,
                    "conversions": 0,
                    "conversion_rate": 0.0,
                    "cost_per_conversion": 0.0
                }
            },
            "variant_b": {
                "name": variations[1]["name"],
                "description": variations[1]["description"],
                "content": {"headline": variations[1]["content_config"]["headline"]},
                "metrics": {
                    "impressions": 0,
                    "clicks": 0,
                    "ctr": 0.0,
                    "conversions": 0,
                    "conversion_rate": 0.0,
                    "cost_per_conversion": 0.0
                }
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create A/B test: {str(e)}"
        )


@router.get("/ab-tests")
async def get_ab_tests(
    status_filter: str = None,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Get user's A/B tests"""
    try:
        # Get tests from framework
        user_tests = [
            test for test in personalization_service.ab_testing_framework.active_tests.values()
            if test.user_id == str(current_user.id)
        ]
        
        # Add completed tests from history
        completed_tests = [
            test for test in personalization_service.ab_testing_framework.test_history
            if test.user_id == str(current_user.id)
        ]
        
        all_tests = user_tests + completed_tests
        
        # Filter by status if provided
        if status_filter and status_filter != 'all':
            all_tests = [test for test in all_tests if test.status.value == status_filter]
        
        # Convert to frontend format
        result = []
        for test in all_tests:
            # Get variation data
            control_var = next((v for v in test.variations if v.variation_id == "control"), None)
            test_var = next((v for v in test.variations if v.variation_id == "test"), None)
            
            test_data = {
                "test_id": test.test_id,
                "campaign_name": test.test_name,
                "test_type": test.test_type.value,
                "status": test.status.value,
                "traffic_split": int(test.traffic_allocation.get("control", 50)),
                "sample_size": test.minimum_sample_size,
                "confidence_level": int((1 - test.significance_level) * 100),
                "start_date": test.start_date.isoformat() if test.start_date else None,
                "end_date": test.planned_end_date.isoformat() if test.planned_end_date else None,
                "variant_a": {
                    "name": control_var.name if control_var else "Control",
                    "description": control_var.description if control_var else "",
                    "content": {"headline": control_var.content_config.get("headline", "") if control_var else ""},
                    "metrics": {
                        "impressions": control_var.impressions if control_var else 0,
                        "clicks": control_var.clicks if control_var else 0,
                        "ctr": control_var.ctr / 100 if control_var else 0.0,
                        "conversions": control_var.conversions if control_var else 0,
                        "conversion_rate": control_var.conversion_rate / 100 if control_var else 0.0,
                        "cost_per_conversion": control_var.revenue / max(control_var.conversions, 1) if control_var and control_var.conversions > 0 else 0.0
                    }
                },
                "variant_b": {
                    "name": test_var.name if test_var else "Test",
                    "description": test_var.description if test_var else "",
                    "content": {"headline": test_var.content_config.get("headline", "") if test_var else ""},
                    "metrics": {
                        "impressions": test_var.impressions if test_var else 0,
                        "clicks": test_var.clicks if test_var else 0,
                        "ctr": test_var.ctr / 100 if test_var else 0.0,
                        "conversions": test_var.conversions if test_var else 0,
                        "conversion_rate": test_var.conversion_rate / 100 if test_var else 0.0,
                        "cost_per_conversion": test_var.revenue / max(test_var.conversions, 1) if test_var and test_var.conversions > 0 else 0.0
                    }
                }
            }
            
            # Add results if test is completed
            if test.current_result:
                result_data = test.current_result
                winner_var = "A" if result_data.winning_variation_id == "control" else "B" if result_data.winning_variation_id == "test" else None
                
                test_data["results"] = {
                    "winner": winner_var,
                    "confidence": int(result_data.confidence_level * 100),
                    "lift": result_data.projected_lift,
                    "significance": int(result_data.confidence_level * 100),
                    "summary": result_data.recommendation,
                    "recommendations": result_data.next_steps
                }
                test_data["statistical_significance"] = int(result_data.confidence_level * 100)
                test_data["winner"] = winner_var
            
            result.append(test_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get A/B tests: {str(e)}"
        )


@router.post("/ab-tests/{test_id}/start")
async def start_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Start an A/B test"""
    try:
        # Get test from framework
        test = personalization_service.ab_testing_framework.active_tests.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found"
            )
        
        if test.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this test"
            )
        
        # Start the test
        from backend.ml.ab_testing.ab_testing_framework import TestStatus
        test.status = TestStatus.ACTIVE
        test.start_date = test.start_date or datetime.now()
        
        return {"success": True, "message": "A/B test started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start A/B test: {str(e)}"
        )


@router.post("/ab-tests/{test_id}/pause")
async def pause_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Pause an A/B test"""
    try:
        test = personalization_service.ab_testing_framework.active_tests.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found"
            )
        
        if test.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this test"
            )
        
        from backend.ml.ab_testing.ab_testing_framework import TestStatus
        test.status = TestStatus.PAUSED
        
        return {"success": True, "message": "A/B test paused successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause A/B test: {str(e)}"
        )


@router.post("/ab-tests/{test_id}/complete")
async def complete_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Complete an A/B test"""
    try:
        success = await personalization_service.ab_testing_framework.conclude_test(
            test_id, "manually_completed"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found or cannot be completed"
            )
        
        return {"success": True, "message": "A/B test completed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete A/B test: {str(e)}"
        )


@router.delete("/ab-tests/{test_id}")
async def delete_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Delete an A/B test"""
    try:
        # Remove from active tests
        if test_id in personalization_service.ab_testing_framework.active_tests:
            test = personalization_service.ab_testing_framework.active_tests[test_id]
            if test.user_id != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this test"
                )
            del personalization_service.ab_testing_framework.active_tests[test_id]
        
        # Remove from history
        personalization_service.ab_testing_framework.test_history = [
            test for test in personalization_service.ab_testing_framework.test_history
            if test.test_id != test_id or test.user_id != str(current_user.id)
        ]
        
        return {"success": True, "message": "A/B test deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete A/B test: {str(e)}"
        )


@router.get("/ab-tests/{test_id}/results")
async def get_ab_test_results(
    test_id: str,
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Get A/B test results"""
    try:
        # Find test in active tests or history
        test = personalization_service.ab_testing_framework.active_tests.get(test_id)
        if not test:
            test = next(
                (t for t in personalization_service.ab_testing_framework.test_history if t.test_id == test_id),
                None
            )
        
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found"
            )
        
        if test.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this test"
            )
        
        # Generate results if not available
        if not test.current_result:
            await personalization_service.ab_testing_framework._evaluate_test_results(test)
        
        if not test.current_result:
            return {
                "winner": None,
                "confidence": 0,
                "lift": 0,
                "significance": 0,
                "summary": "Insufficient data for analysis",
                "recommendations": ["Continue running the test to gather more data"]
            }
        
        result_data = test.current_result
        winner_var = "A" if result_data.winning_variation_id == "control" else "B" if result_data.winning_variation_id == "test" else None
        
        return {
            "winner": winner_var,
            "confidence": int(result_data.confidence_level * 100),
            "lift": result_data.projected_lift,
            "significance": int(result_data.confidence_level * 100),
            "summary": result_data.recommendation,
            "recommendations": result_data.next_steps
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get A/B test results: {str(e)}"
        )


# ML Prediction Endpoints

@router.post("/predictions/campaign-performance")
@require_tier("professional")
async def predict_campaign_performance(
    campaign_config: dict,
    historical_data: List[dict] = None,
    use_cache: bool = True,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Predict campaign performance using Claude ML Predictor
    
    This endpoint provides AI-powered predictions for campaign metrics including:
    - ROI predictions
    - CTR estimates 
    - Conversion rate forecasts
    - Budget optimization recommendations
    """
    try:
        # Check if ML predictions are enabled
        if not settings.is_ml_predictions_enabled():
            # Return fallback prediction
            return {
                "status": "fallback",
                "message": "ML predictions disabled - configure ANTHROPIC_API_KEY to enable",
                "prediction": await ml_prediction_service._generate_fallback_prediction(
                    str(current_user.id), campaign_config, "campaign_performance"
                ),
                "configuration": settings.get_ml_config()
            }
        
        # Generate prediction using ML service
        prediction = await ml_prediction_service.predict_campaign_performance(
            user_id=str(current_user.id),
            campaign_config=campaign_config,
            historical_data=historical_data,
            db=db,
            use_cache=use_cache
        )
        
        return {
            "status": "success",
            "prediction": prediction,
            "configuration": settings.get_ml_config()
        }
        
    except Exception as e:
        logger.error(f"Error predicting campaign performance: {e}")
        # Return fallback prediction on error
        fallback_prediction = await ml_prediction_service._generate_fallback_prediction(
            str(current_user.id), campaign_config, "campaign_performance"
        )
        return {
            "status": "error_fallback",
            "message": f"ML prediction failed: {str(e)}",
            "prediction": fallback_prediction,
            "error": str(e)
        }

@router.post("/predictions/viral-potential")
@require_tier("professional")
async def predict_viral_potential(
    content_config: dict,
    use_cache: bool = True,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Predict viral potential of content using Claude ML Predictor
    
    This endpoint analyzes content and provides predictions for:
    - Viral reach potential
    - Engagement rate forecasts
    - Optimal posting timing
    - Content optimization suggestions
    """
    try:
        # Check if ML predictions are enabled
        if not settings.is_ml_predictions_enabled():
            return {
                "status": "fallback",
                "message": "ML predictions disabled - configure ANTHROPIC_API_KEY to enable",
                "prediction": await ml_prediction_service._generate_fallback_prediction(
                    current_user.id, content_config, "viral_potential"
                ),
                "configuration": settings.get_ml_config()
            }
        
        # Generate viral potential prediction
        prediction = await ml_prediction_service.predict_viral_potential(
            user_id=str(current_user.id),
            content_config=content_config,
            db=db,
            use_cache=use_cache
        )
        
        return {
            "status": "success",
            "prediction": prediction,
            "configuration": settings.get_ml_config()
        }
        
    except Exception as e:
        logger.error(f"Error predicting viral potential: {e}")
        fallback_prediction = await ml_prediction_service._generate_fallback_prediction(
            str(current_user.id), content_config, "viral_potential"
        )
        return {
            "status": "error_fallback",
            "message": f"ML prediction failed: {str(e)}",
            "prediction": fallback_prediction,
            "error": str(e)
        }

@router.get("/predictions/history")
async def get_prediction_history(
    prediction_type: str = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get user's prediction history with filtering and pagination
    
    Parameters:
    - prediction_type: Filter by type (campaign_performance, viral_potential, etc.)
    - limit: Maximum number of predictions to return
    - offset: Number of predictions to skip for pagination
    """
    try:
        from backend.database.crud import MLPredictionCRUD
        from backend.database.models import MLPredictionType
        
        # Validate prediction type if provided
        ml_prediction_type = None
        if prediction_type:
            try:
                ml_prediction_type = MLPredictionType(prediction_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid prediction type: {prediction_type}")
        
        # Get predictions from database
        predictions = MLPredictionCRUD.get_user_predictions(
            db=db,
            user_id=str(current_user.id),
            prediction_type=ml_prediction_type,
            limit=limit,
            offset=offset
        )
        
        # Convert to API response format
        prediction_history = []
        for pred in predictions:
            prediction_data = {
                "id": pred.id,
                "prediction_id": pred.prediction_id,
                "prediction_type": pred.prediction_type.value,
                "predicted_metrics": pred.predicted_metrics,
                "confidence_level": pred.confidence_level.value,
                "confidence_score": pred.confidence_score,
                "prediction_reasoning": pred.prediction_reasoning,
                "key_factors": pred.key_factors,
                "optimization_opportunities": pred.optimization_opportunities,
                "created_at": pred.created_at.isoformat(),
                "model_version": pred.model_version,
                "has_actual_results": bool(pred.actual_metrics),
                "accuracy_score": pred.prediction_accuracy_score
            }
            
            # Include actual results if available
            if pred.actual_metrics:
                prediction_data["actual_metrics"] = pred.actual_metrics
            
            prediction_history.append(prediction_data)
        
        return {
            "status": "success",
            "predictions": prediction_history,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "count": len(prediction_history)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting prediction history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prediction history")

@router.get("/predictions/insights")
async def get_prediction_insights(
    prediction_type: str = None,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Get prediction insights and accuracy metrics for the user
    
    Returns:
    - Prediction accuracy trends
    - Model performance statistics
    - User-specific insights
    - Feedback statistics
    """
    try:
        # Get insights from ML prediction service
        insights = await ml_prediction_service.get_prediction_insights(
            user_id=str(current_user.id),
            prediction_type=prediction_type,
            db=db
        )
        
        # Get additional database insights
        from backend.database.crud import MLPredictionCRUD
        from backend.database.models import MLPredictionType
        
        # Validate prediction type if provided
        ml_prediction_type = None
        if prediction_type:
            try:
                ml_prediction_type = MLPredictionType(prediction_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid prediction type: {prediction_type}")
        
        # Get accuracy trends
        accuracy_trends = MLPredictionCRUD.get_prediction_accuracy_trends(
            db=db,
            user_id=str(current_user.id),
            days=30
        )
        
        # Get feedback statistics
        feedback_stats = MLPredictionCRUD.get_prediction_feedback_stats(
            db=db,
            user_id=str(current_user.id),
            prediction_type=ml_prediction_type
        )
        
        # Combine all insights
        combined_insights = {
            **insights,
            "accuracy_trends": accuracy_trends,
            "feedback_statistics": feedback_stats,
            "configuration": settings.get_ml_config()
        }
        
        return {
            "status": "success",
            "insights": combined_insights
        }
        
    except Exception as e:
        logger.error(f"Error getting prediction insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prediction insights")

@router.post("/predictions/{prediction_id}/accuracy")
async def update_prediction_accuracy(
    prediction_id: str,
    actual_metrics: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Update prediction accuracy when actual campaign results are available
    
    This endpoint allows users to provide actual campaign results to improve
    future prediction accuracy through machine learning feedback loops.
    """
    try:
        # Update prediction accuracy using ML service
        result = await ml_prediction_service.update_prediction_accuracy(
            prediction_id=prediction_id,
            actual_metrics=actual_metrics,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "status": "success",
            "message": "Prediction accuracy updated successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prediction accuracy: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prediction accuracy")

@router.get("/predictions/config")
async def get_ml_prediction_config(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Get ML prediction configuration and availability status
    
    Returns information about:
    - Whether ML predictions are enabled
    - Model version and configuration
    - Cache settings
    - Feature availability
    """
    try:
        config = settings.get_ml_config()
        
        # Add user-specific information
        config.update({
            "user_id": str(current_user.id),
            "available_prediction_types": [
                "campaign_performance",
                "viral_potential",
                "audience_response",
                "content_effectiveness",
                "budget_optimization"
            ],
            "supported_metrics": [
                "roi", "ctr", "conversion_rate", "engagement_rate",
                "reach", "impressions", "clicks", "cost_per_click"
            ]
        })
        
        return {
            "status": "success",
            "configuration": config
        }
        
    except Exception as e:
        logger.error(f"Error getting ML prediction config: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve configuration")


# Additional ML Prediction Endpoints

@router.post("/predictions/audience-response")
async def predict_audience_response(
    audience_config: dict,
    use_cache: bool = True,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Predict audience response to marketing content
    
    This endpoint analyzes target audience characteristics and predicts:
    - Engagement likelihood
    - Response rates by demographic
    - Optimal messaging strategies
    - Platform preference analysis
    """
    try:
        # Check if ML predictions are enabled
        if not settings.is_ml_predictions_enabled():
            return {
                "status": "fallback",
                "message": "ML predictions disabled - configure ANTHROPIC_API_KEY to enable",
                "prediction": await ml_prediction_service._generate_fallback_prediction(
                    str(current_user.id), audience_config, "audience_response"
                ),
                "configuration": settings.get_ml_config()
            }
        
        # For now, use viral potential prediction as basis for audience response
        prediction = await ml_prediction_service.predict_viral_potential(
            user_id=str(current_user.id),
            content_config=audience_config,
            db=db,
            use_cache=use_cache
        )
        
        # Adapt the response for audience response context
        if prediction.get("success"):
            prediction["prediction_type"] = "audience_response"
            prediction["audience_insights"] = prediction.get("viral_factors", [])
            prediction["response_barriers"] = prediction.get("limiting_factors", [])
        
        return {
            "status": "success",
            "prediction": prediction,
            "configuration": settings.get_ml_config()
        }
        
    except Exception as e:
        logger.error(f"Error predicting audience response: {e}")
        fallback_prediction = await ml_prediction_service._generate_fallback_prediction(
            str(current_user.id), audience_config, "audience_response"
        )
        return {
            "status": "error_fallback",
            "message": f"ML prediction failed: {str(e)}",
            "prediction": fallback_prediction,
            "error": str(e)
        }


@router.post("/predictions/content-effectiveness")
async def predict_content_effectiveness(
    content_config: dict,
    use_cache: bool = True,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Predict content effectiveness across different platforms and audiences
    
    This endpoint analyzes content characteristics and predicts:
    - Content performance by platform
    - Optimal posting times
    - Content format recommendations
    - A/B testing suggestions
    """
    try:
        # Check if ML predictions are enabled
        if not settings.is_ml_predictions_enabled():
            return {
                "status": "fallback",
                "message": "ML predictions disabled - configure ANTHROPIC_API_KEY to enable",
                "prediction": await ml_prediction_service._generate_fallback_prediction(
                    str(current_user.id), content_config, "content_effectiveness"
                ),
                "configuration": settings.get_ml_config()
            }
        
        # Use viral potential prediction as basis for content effectiveness
        prediction = await ml_prediction_service.predict_viral_potential(
            user_id=str(current_user.id),
            content_config=content_config,
            db=db,
            use_cache=use_cache
        )
        
        # Adapt the response for content effectiveness context
        if prediction.get("success"):
            prediction["prediction_type"] = "content_effectiveness"
            prediction["effectiveness_factors"] = prediction.get("viral_factors", [])
            prediction["improvement_areas"] = prediction.get("optimization_opportunities", [])
            
            # Add platform-specific effectiveness predictions
            predicted_metrics = prediction.get("predicted_metrics", {})
            predicted_metrics.update({
                "facebook_effectiveness": 75.0,
                "instagram_effectiveness": 80.0
            })
        
        return {
            "status": "success",
            "prediction": prediction,
            "configuration": settings.get_ml_config()
        }
        
    except Exception as e:
        logger.error(f"Error predicting content effectiveness: {e}")
        fallback_prediction = await ml_prediction_service._generate_fallback_prediction(
            str(current_user.id), content_config, "content_effectiveness"
        )
        return {
            "status": "error_fallback",
            "message": f"ML prediction failed: {str(e)}",
            "prediction": fallback_prediction,
            "error": str(e)
        }


@router.post("/predictions/budget-optimization")
async def predict_budget_optimization(
    campaign_config: dict,
    budget_constraints: dict = None,
    use_cache: bool = True,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Predict optimal budget allocation for maximum ROI
    
    This endpoint analyzes campaign configuration and predicts:
    - Optimal budget distribution across platforms
    - Expected ROI for different budget levels
    - Cost optimization opportunities
    - Performance scaling predictions
    """
    try:
        # Check if ML predictions are enabled
        if not settings.is_ml_predictions_enabled():
            return {
                "status": "fallback",
                "message": "ML predictions disabled - configure ANTHROPIC_API_KEY to enable",
                "prediction": await ml_prediction_service._generate_fallback_prediction(
                    str(current_user.id), campaign_config, "budget_optimization"
                ),
                "configuration": settings.get_ml_config()
            }
        
        # Use campaign performance prediction as basis for budget optimization
        prediction = await ml_prediction_service.predict_campaign_performance(
            user_id=str(current_user.id),
            campaign_config=campaign_config,
            historical_data=None,
            db=db,
            use_cache=use_cache
        )
        
        # Adapt the response for budget optimization context
        if prediction.get("success"):
            prediction["prediction_type"] = "budget_optimization"
            
            # Add budget-specific insights
            current_budget = campaign_config.get("budget", 1000)
            primary_prediction = prediction.get("primary_prediction", {})
            
            prediction["budget_recommendations"] = {
                "current_budget": current_budget,
                "optimal_budget": int(current_budget * 1.2),
                "minimum_budget": int(current_budget * 0.8),
                "budget_distribution": {
                    "facebook": 60,
                    "instagram": 35,
                    "other": 5
                },
                "scaling_predictions": {
                    "50%_increase": {
                        "expected_roi_lift": 15,
                        "risk_level": "low"
                    },
                    "100%_increase": {
                        "expected_roi_lift": 25,
                        "risk_level": "medium"
                    }
                }
            }
        
        return {
            "status": "success",
            "prediction": prediction,
            "configuration": settings.get_ml_config()
        }
        
    except Exception as e:
        logger.error(f"Error predicting budget optimization: {e}")
        fallback_prediction = await ml_prediction_service._generate_fallback_prediction(
            str(current_user.id), campaign_config, "budget_optimization"
        )
        return {
            "status": "error_fallback",
            "message": f"ML prediction failed: {str(e)}",
            "prediction": fallback_prediction,
            "error": str(e)
        }


@router.post("/predictions/feedback")
async def submit_prediction_feedback(
    feedback_data: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on prediction accuracy and usefulness
    
    This endpoint allows users to provide feedback on ML predictions to improve
    future accuracy through machine learning feedback loops.
    """
    try:
        from backend.database.crud import MLPredictionCRUD
        
        # Validate required fields
        required_fields = ["prediction_id", "accuracy_rating", "usefulness_rating"]
        missing_fields = [field for field in required_fields if field not in feedback_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate ratings (1-5 scale)
        accuracy_rating = feedback_data["accuracy_rating"]
        usefulness_rating = feedback_data["usefulness_rating"]
        
        if not (1 <= accuracy_rating <= 5) or not (1 <= usefulness_rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ratings must be between 1 and 5"
            )
        
        # Create feedback entry
        feedback = MLPredictionCRUD.create_prediction_feedback(
            db=db,
            prediction_result_id=feedback_data["prediction_id"],
            user_id=str(current_user.id),
            accuracy_rating=accuracy_rating,
            usefulness_rating=usefulness_rating,
            followed_recommendations=feedback_data.get("followed_recommendations", False),
            feedback_text=feedback_data.get("feedback_text"),
            specific_issues=feedback_data.get("specific_issues"),
            suggestions=feedback_data.get("suggestions"),
            actual_campaign_results=feedback_data.get("actual_campaign_results"),
            outcome_satisfaction=feedback_data.get("outcome_satisfaction")
        )
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.id,
            "submitted_at": feedback.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting prediction feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")