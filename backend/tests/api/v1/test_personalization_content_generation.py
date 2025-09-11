"""
API tests for Personalization Content Generation endpoints
Tests the REST API endpoints that expose dynamic content generation functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from services.personalization_service import EnhancedPersonalizationService
from ml.content_generation.dynamic_content_generator import AdaptiveContentSet


@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    user = Mock()
    user.id = 12345
    user.email = "test@example.com"
    user.is_verified = True
    return user


@pytest.fixture
def sample_image_strategy_request():
    """Sample image strategy request payload"""
    return {
        "campaign_brief": "Summer fitness bootcamp promotion",
        "business_description": "Outdoor fitness studio specializing in HIIT workouts",
        "target_audience_description": "Young professionals aged 22-35 interested in fitness",
        "unique_value_proposition": "High-intensity workouts that deliver results in 4 weeks",
        "preferred_style": "energetic"
    }


@pytest.fixture
def sample_video_strategy_request():
    """Sample video strategy request payload"""
    return {
        "campaign_brief": "30-second fitness transformation showcase",
        "business_description": "Premium fitness studio with personal trainers",
        "target_audience_description": "Busy executives who want quick fitness solutions",
        "unique_value_proposition": "See results in just 30 minutes per session",
        "preferred_style": "cinematic",
        "aspect_ratios": ["16:9", "9:16"]
    }


@pytest.fixture
def mock_content_generation_response():
    """Mock successful content generation response"""
    return {
        "content_variations": [
            {
                "variation_id": "control",
                "variation_name": "Control Version",
                "visual_prompt": "Professional fitness studio with modern equipment",
                "caption": "Transform your fitness journey with our expert trainers! 💪",
                "hashtags": ["#fitness", "#transformation", "#health"],
                "color_palette": ["#FF6B35", "#004E89", "#FFFFFF", "#1A1A1A"],
                "aspect_ratio": "1:1",
                "predicted_engagement": 2.3,
                "predicted_ctr": 1.8,
                "predicted_conversion": 7.5
            },
            {
                "variation_id": "demographic_millennial", 
                "variation_name": "Millennial-Optimized",
                "visual_prompt": "Modern fitness space with young professionals working out",
                "caption": "Achieve your fitness goals while balancing career success! 🚀 #WorkLifeBalance",
                "hashtags": ["#MillennialFitness", "#Goals", "#Balance", "#Success"],
                "color_palette": ["#00D4AA", "#2E86AB", "#F18F01", "#FFFFFF"],
                "aspect_ratio": "1:1",
                "predicted_engagement": 3.1,
                "predicted_ctr": 2.4,
                "predicted_conversion": 9.2
            }
        ],
        "ab_test_config": {
            "test_name": "Fitness Campaign A/B Test",
            "traffic_split": {"control": 40, "variation_1": 60},
            "primary_metric": "conversion_rate",
            "estimated_test_duration": 14
        },
        "personalization_insights": [
            "Content optimized for millennial audience preferences",
            "Instagram-native format and hashtags included",
            "Indian market cultural elements incorporated"
        ]
    }


@pytest.mark.api
class TestPersonalizationProfileEndpoints:
    """Test profile management endpoints for content generation"""
    
    def test_create_profile_success(self, client, mock_user):
        """Test successful profile creation"""
        profile_data = {
            "business_size": "smb",
            "industry": "fitness", 
            "business_name": "Mumbai Fitness Pro",
            "monthly_budget": "medium",
            "primary_objective": "lead_generation",
            "target_age_groups": ["millennial", "gen_z"],
            "platform_priorities": ["instagram", "facebook"],
            "brand_voice": "authentic",
            "content_preference": "mixed"
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'create_comprehensive_user_profile', new_callable=AsyncMock) as mock_create:
                mock_create.return_value = {"user_profile": {"user_id": "12345", **profile_data}}
                
                response = client.post(
                    "/api/v1/personalization/profile",
                    json=profile_data
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "data" in data
                mock_create.assert_called_once()
    
    def test_create_profile_missing_fields(self, client, mock_user):
        """Test profile creation with missing required fields"""
        incomplete_data = {
            "business_size": "smb",
            "industry": "fitness"
            # Missing other required fields
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            response = client.post(
                "/api/v1/personalization/profile",
                json=incomplete_data
            )
            
            # Should still succeed as service handles validation
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    def test_get_profile_success(self, client, mock_user):
        """Test successful profile retrieval"""
        mock_profile = {
            "user_id": "12345",
            "industry": "fitness",
            "business_name": "Test Studio"
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'personalization_engine') as mock_engine:
                mock_engine.user_profiles.get.return_value = mock_profile
                
                response = client.get("/api/v1/personalization/profile")
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert data["data"] == mock_profile
    
    def test_get_profile_not_found(self, client, mock_user):
        """Test profile retrieval when profile doesn't exist"""
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'personalization_engine') as mock_engine:
                mock_engine.user_profiles.get.return_value = None
                
                response = client.get("/api/v1/personalization/profile")
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
                data = response.json()
                assert "Profile not found" in data["detail"]


@pytest.mark.api
class TestContentGenerationEndpoints:
    """Test content generation API endpoints"""
    
    def test_generate_image_strategy_success(self, client, mock_user, sample_image_strategy_request, mock_content_generation_response):
        """Test successful image strategy generation"""
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'get_personalized_image_strategy', new_callable=AsyncMock) as mock_strategy:
                mock_strategy.return_value = mock_content_generation_response
                
                response = client.post(
                    "/api/v1/personalization/image-strategy",
                    json=sample_image_strategy_request
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "content_variations" in data["data"]
                assert "ab_test_config" in data["data"]
                assert len(data["data"]["content_variations"]) >= 2
                
                # Verify service was called with correct parameters
                mock_strategy.assert_called_once_with(
                    user_id="12345",
                    campaign_brief=sample_image_strategy_request["campaign_brief"],
                    business_description=sample_image_strategy_request["business_description"],
                    target_audience_description=sample_image_strategy_request["target_audience_description"],
                    unique_value_proposition=sample_image_strategy_request["unique_value_proposition"],
                    preferred_style=sample_image_strategy_request["preferred_style"],
                    aspect_ratios=None
                )
    
    def test_generate_image_strategy_missing_fields(self, client, mock_user):
        """Test image strategy generation with missing required fields"""
        incomplete_request = {
            "campaign_brief": "fitness program",
            # Missing other required fields
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            response = client.post(
                "/api/v1/personalization/image-strategy",
                json=incomplete_request
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Missing required fields" in data["detail"]
    
    def test_generate_video_strategy_success(self, client, mock_user, sample_video_strategy_request):
        """Test successful video strategy generation"""
        mock_video_response = {
            "video_strategies": [
                {
                    "aspect_ratio": "16:9",
                    "visual_prompt": "Cinematic fitness transformation sequence",
                    "caption": "30 seconds to see your transformation! 🎥",
                    "suggested_duration": 30,
                    "hashtags": ["#transformation", "#fitness", "#video"]
                },
                {
                    "aspect_ratio": "9:16", 
                    "visual_prompt": "Vertical fitness story for mobile",
                    "caption": "Swipe up for fitness success! 📱",
                    "suggested_duration": 15,
                    "hashtags": ["#fitstory", "#mobile", "#vertical"]
                }
            ],
            "personalization_insights": [
                "Video content optimized for executive audience",
                "Multiple aspect ratios for cross-platform use"
            ]
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'get_personalized_video_strategy', new_callable=AsyncMock) as mock_strategy:
                mock_strategy.return_value = mock_video_response
                
                response = client.post(
                    "/api/v1/personalization/video-strategy",
                    json=sample_video_strategy_request
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "video_strategies" in data["data"]
                assert len(data["data"]["video_strategies"]) == 2
                
                # Verify both aspect ratios were generated
                aspect_ratios = [vs["aspect_ratio"] for vs in data["data"]["video_strategies"]]
                assert "16:9" in aspect_ratios
                assert "9:16" in aspect_ratios
    
    def test_generate_campaign_strategy_success(self, client, mock_user):
        """Test comprehensive campaign strategy generation"""
        strategy_request = {
            "campaign_brief": "Complete fitness studio marketing campaign",
            "objective_override": "brand_awareness"
        }
        
        mock_comprehensive_response = {
            "campaign_recommendations": [
                {"strategy_type": "image_heavy", "confidence": 0.85},
                {"strategy_type": "video_focused", "confidence": 0.92}
            ],
            "content_variations": [
                {
                    "variation_id": "comprehensive_1",
                    "visual_prompt": "Multi-platform fitness content",
                    "caption": "Your fitness journey starts here! 💪🚀",
                    "hashtags": ["#fitnessjourney", "#comprehensive"]
                }
            ],
            "ab_testing_recommendations": {
                "primary_test": "image_vs_video",
                "traffic_allocation": {"image": 50, "video": 50},
                "success_metrics": ["engagement_rate", "conversion_rate"]
            }
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'get_personalized_campaign_strategy', new_callable=AsyncMock) as mock_strategy:
                mock_strategy.return_value = mock_comprehensive_response
                
                response = client.post(
                    "/api/v1/personalization/campaign-strategy",
                    json=strategy_request
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "campaign_recommendations" in data["data"]
                assert "ab_testing_recommendations" in data["data"]
    
    def test_content_generation_service_error(self, client, mock_user, sample_image_strategy_request):
        """Test handling of service-level errors"""
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'get_personalized_image_strategy', new_callable=AsyncMock) as mock_strategy:
                mock_strategy.side_effect = ValueError("User profile not found")
                
                response = client.post(
                    "/api/v1/personalization/image-strategy",
                    json=sample_image_strategy_request
                )
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                data = response.json()
                assert "Failed to generate strategy" in data["detail"]


@pytest.mark.api
class TestContentGenerationAuthentication:
    """Test authentication requirements for content generation endpoints"""
    
    def test_image_strategy_requires_authentication(self, client, sample_image_strategy_request):
        """Test that image strategy endpoint requires authentication"""
        response = client.post(
            "/api/v1/personalization/image-strategy",
            json=sample_image_strategy_request
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_video_strategy_requires_authentication(self, client, sample_video_strategy_request):
        """Test that video strategy endpoint requires authentication"""
        response = client.post(
            "/api/v1/personalization/video-strategy", 
            json=sample_video_strategy_request
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_profile_endpoints_require_authentication(self, client):
        """Test that profile endpoints require authentication"""
        # Test profile creation
        response = client.post(
            "/api/v1/personalization/profile",
            json={"industry": "fitness"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test profile retrieval
        response = client.get("/api/v1/personalization/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestContentGenerationDataValidation:
    """Test input validation for content generation endpoints"""
    
    def test_image_strategy_field_validation(self, client, mock_user):
        """Test field validation for image strategy requests"""
        test_cases = [
            # Missing campaign_brief
            {
                "request": {
                    "business_description": "test business",
                    "target_audience_description": "test audience",
                    "unique_value_proposition": "test value"
                },
                "missing_field": "campaign_brief"
            },
            # Missing business_description  
            {
                "request": {
                    "campaign_brief": "test campaign",
                    "target_audience_description": "test audience",
                    "unique_value_proposition": "test value"
                },
                "missing_field": "business_description"
            },
            # Missing target_audience_description
            {
                "request": {
                    "campaign_brief": "test campaign",
                    "business_description": "test business",
                    "unique_value_proposition": "test value"
                },
                "missing_field": "target_audience_description"
            },
            # Missing unique_value_proposition
            {
                "request": {
                    "campaign_brief": "test campaign",
                    "business_description": "test business",
                    "target_audience_description": "test audience"
                },
                "missing_field": "unique_value_proposition"
            }
        ]
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            for test_case in test_cases:
                response = client.post(
                    "/api/v1/personalization/image-strategy",
                    json=test_case["request"]
                )
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
                data = response.json()
                assert test_case["missing_field"] in data["detail"]
    
    def test_video_strategy_field_validation(self, client, mock_user):
        """Test field validation for video strategy requests"""
        invalid_request = {
            "campaign_brief": "",  # Empty required field
            "business_description": "test business",
            "target_audience_description": "test audience",
            "unique_value_proposition": "test value"
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            response = client.post(
                "/api/v1/personalization/video-strategy",
                json=invalid_request
            )
            
            # Should fail validation due to empty campaign_brief
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_campaign_strategy_validation(self, client, mock_user):
        """Test validation for campaign strategy requests"""
        invalid_request = {}  # Missing campaign_brief
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            response = client.post(
                "/api/v1/personalization/campaign-strategy",
                json=invalid_request
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Campaign brief is required" in data["detail"]


@pytest.mark.api
class TestContentGenerationResponseFormat:
    """Test response format consistency for content generation endpoints"""
    
    def test_image_strategy_response_structure(self, client, mock_user, sample_image_strategy_request):
        """Test that image strategy responses have consistent structure"""
        expected_response = {
            "content_variations": [
                {
                    "variation_id": "test_variation",
                    "visual_prompt": "test prompt", 
                    "caption": "test caption",
                    "hashtags": ["#test"],
                    "color_palette": ["#FF0000"],
                    "predicted_engagement": 2.5
                }
            ],
            "ab_test_config": {
                "test_name": "Test A/B",
                "traffic_split": {"control": 50, "variation": 50}
            }
        }
        
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'get_personalized_image_strategy', new_callable=AsyncMock) as mock_strategy:
                mock_strategy.return_value = expected_response
                
                response = client.post(
                    "/api/v1/personalization/image-strategy",
                    json=sample_image_strategy_request
                )
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                
                # Verify consistent API response wrapper
                assert "success" in data
                assert "data" in data
                assert data["success"] is True
                
                # Verify content structure
                content_data = data["data"]
                assert "content_variations" in content_data
                assert "ab_test_config" in content_data
                
                # Verify content variation structure
                if content_data["content_variations"]:
                    variation = content_data["content_variations"][0]
                    required_fields = ["variation_id", "visual_prompt", "caption", "hashtags"]
                    for field in required_fields:
                        assert field in variation
    
    def test_error_response_format(self, client, mock_user):
        """Test that error responses have consistent format"""
        with patch('app.dependencies.get_current_verified_user', return_value=mock_user):
            with patch.object(EnhancedPersonalizationService, 'get_personalized_image_strategy', new_callable=AsyncMock) as mock_strategy:
                mock_strategy.side_effect = Exception("Test error")
                
                response = client.post(
                    "/api/v1/personalization/image-strategy",
                    json={
                        "campaign_brief": "test",
                        "business_description": "test", 
                        "target_audience_description": "test",
                        "unique_value_proposition": "test"
                    }
                )
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                data = response.json()
                
                # Verify error response structure
                assert "detail" in data
                assert isinstance(data["detail"], str)
                assert "Failed to generate strategy" in data["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])