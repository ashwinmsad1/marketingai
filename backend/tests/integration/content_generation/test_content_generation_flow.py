"""
Integration tests for Dynamic Content Generator
Tests end-to-end content generation flow and service integration
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from services.personalization_service import EnhancedPersonalizationService
from ml.content_generation.dynamic_content_generator import DynamicContentGenerator, AdaptiveContentSet
from engines.personalization_engine import (
    PersonalizationEngine, 
    UserProfile, 
    AgeGroup, 
    BrandVoice, 
    CampaignObjective
)


@pytest.fixture
def mock_user_profile_data():
    """Sample user profile data for integration testing"""
    return {
        "business_size": "smb",
        "industry": "fitness",
        "business_name": "Mumbai Fitness Studio",
        "monthly_budget": "small",
        "primary_objective": "lead_generation",
        "target_age_groups": ["millennial", "gen_z"],
        "platform_priorities": ["instagram", "facebook"],
        "brand_voice": "authentic",
        "content_preference": "mixed"
    }


@pytest.fixture
def sample_strategy_request():
    """Sample strategy request for API testing"""
    return {
        "campaign_brief": "30-day fitness transformation program for working professionals",
        "business_description": "Modern fitness studio in Mumbai offering personalized training",
        "target_audience_description": "Working professionals aged 25-35 who struggle with work-life balance",
        "unique_value_proposition": "Quick 30-minute sessions that fit into busy schedules",
        "preferred_style": "authentic"
    }


@pytest.mark.integration
@pytest.mark.asyncio
class TestContentGenerationServiceIntegration:
    """Test integration between personalization service and content generator"""
    
    async def test_full_content_generation_flow(self, mock_user_profile_data, sample_strategy_request):
        """Test complete content generation flow from user input to generated content"""
        with patch('os.getenv', return_value=None):  # No API keys for testing
            # Initialize service
            service = EnhancedPersonalizationService()
            
            # Create user profile
            user_id = "integration_test_user"
            profile = await service.personalization_engine.create_user_profile(
                user_id, mock_user_profile_data
            )
            
            assert profile is not None
            assert profile.user_id == user_id
            assert profile.industry == "fitness"
            
            # Generate personalized content strategy
            with patch.object(service.content_generator, '_claude_generate_prompt', return_value="Professional fitness studio content"):
                with patch.object(service.content_generator, '_claude_generate_caption', return_value="Transform your fitness journey! 💪"):
                    with patch.object(service.content_generator, '_claude_generate_hashtags', return_value=["#fitness", "#transformation"]):
                        with patch.object(service.content_generator, '_claude_generate_color_palette', return_value=["#FF5733", "#FFFFFF"]):
                            
                            strategy = await service.get_personalized_image_strategy(
                                user_id=user_id,
                                campaign_brief=sample_strategy_request["campaign_brief"],
                                business_description=sample_strategy_request["business_description"],
                                target_audience_description=sample_strategy_request["target_audience_description"],
                                unique_value_proposition=sample_strategy_request["unique_value_proposition"]
                            )
            
            # Verify strategy generation
            assert strategy is not None
            assert "content_variations" in strategy
            assert len(strategy["content_variations"]) >= 3  # Control + variations
            
            # Verify content variation structure
            for variation in strategy["content_variations"]:
                assert "variation_id" in variation
                assert "visual_prompt" in variation
                assert "caption" in variation
                assert "hashtags" in variation
                assert "color_palette" in variation
                assert "predicted_engagement" in variation
    
    async def test_video_strategy_generation(self, mock_user_profile_data, sample_strategy_request):
        """Test video strategy generation flow"""
        with patch('os.getenv', return_value=None):
            service = EnhancedPersonalizationService()
            
            user_id = "video_test_user"
            await service.personalization_engine.create_user_profile(
                user_id, mock_user_profile_data
            )
            
            with patch.object(service.content_generator, '_claude_generate_prompt', return_value="Dynamic fitness video content"):
                with patch.object(service.content_generator, '_claude_generate_caption', return_value="30 seconds to fitness success! 🎥"):
                    with patch.object(service.content_generator, '_claude_generate_hashtags', return_value=["#fitnessvideos", "#30daychallenge"]):
                        
                        strategy = await service.get_personalized_video_strategy(
                            user_id=user_id,
                            campaign_brief=sample_strategy_request["campaign_brief"],
                            business_description=sample_strategy_request["business_description"],
                            target_audience_description=sample_strategy_request["target_audience_description"],
                            unique_value_proposition=sample_strategy_request["unique_value_proposition"],
                            preferred_style="cinematic",
                            aspect_ratios=["16:9", "9:16"]
                        )
            
            assert strategy is not None
            assert "video_strategies" in strategy
            assert len(strategy["video_strategies"]) >= 2  # Multiple aspect ratios
            
            for video_strategy in strategy["video_strategies"]:
                assert "aspect_ratio" in video_strategy
                assert "visual_prompt" in video_strategy
                assert "suggested_duration" in video_strategy
    
    async def test_ab_testing_integration(self, mock_user_profile_data, sample_strategy_request):
        """Test A/B testing integration with content generation"""
        with patch('os.getenv', return_value=None):
            service = EnhancedPersonalizationService()
            
            user_id = "ab_test_user"
            await service.personalization_engine.create_user_profile(
                user_id, mock_user_profile_data
            )
            
            # Mock content generation
            mock_content_set = Mock(spec=AdaptiveContentSet)
            mock_content_set.content_set_id = "test_content_set"
            mock_content_set.variations = [Mock(), Mock(), Mock()]
            mock_content_set.control_variation = Mock()
            mock_content_set.test_hypothesis = "Test hypothesis"
            mock_content_set.traffic_split = {"control": 0.4, "variation_1": 0.3, "variation_2": 0.3}
            
            with patch.object(service.content_generator, 'generate_personalized_content_variations', return_value=mock_content_set):
                with patch.object(service.ab_testing_framework, 'create_personalized_ab_test', new_callable=AsyncMock) as mock_ab_test:
                    
                    # Generate content and create A/B test
                    content_strategy = await service.get_personalized_campaign_strategy(
                        user_id=user_id,
                        campaign_brief=sample_strategy_request["campaign_brief"]
                    )
                    
                    # Verify A/B test integration
                    assert content_strategy is not None
                    mock_ab_test.assert_called_once()
    
    async def test_performance_learning_integration(self, mock_user_profile_data):
        """Test integration with adaptive learning system"""
        with patch('os.getenv', return_value=None):
            service = EnhancedPersonalizationService()
            
            user_id = "learning_test_user"
            
            # Create profile with campaign history
            profile_data = mock_user_profile_data.copy()
            profile_data["campaign_history"] = [
                {"type": "image", "performance": {"roi": 12, "ctr": 2.1}},
                {"type": "video", "performance": {"roi": 18, "ctr": 3.2}}
            ]
            
            profile = await service.personalization_engine.create_user_profile(
                user_id, profile_data
            )
            
            # Mock learning system interaction
            with patch.object(service.learning_system, 'extract_performance_insights', new_callable=AsyncMock) as mock_insights:
                mock_insights.return_value = [
                    Mock(insight_type="content_effectiveness", recommendation="Use more video content")
                ]
                
                with patch.object(service.content_generator, 'generate_personalized_content_variations', new_callable=AsyncMock) as mock_generate:
                    mock_content_set = Mock(spec=AdaptiveContentSet)
                    mock_generate.return_value = mock_content_set
                    
                    # Generate strategy with learning integration
                    strategy = await service.get_comprehensive_campaign_strategy(
                        user_id=user_id,
                        campaign_brief="fitness program promotion",
                        include_learning_insights=True
                    )
                    
                    # Verify learning system was consulted
                    mock_insights.assert_called_once()
                    mock_generate.assert_called_once()


@pytest.mark.integration
@pytest.mark.asyncio
class TestContentGenerationAPIIntegration:
    """Test API-level integration for content generation"""
    
    async def test_personalization_profile_to_content_flow(self, mock_user_profile_data):
        """Test flow from profile creation to content generation via API simulation"""
        with patch('os.getenv', return_value=None):
            service = EnhancedPersonalizationService()
            
            # Simulate API profile creation
            user_id = "api_integration_user"
            profile_response = await service.create_comprehensive_user_profile(
                user_id=user_id,
                profile_data=mock_user_profile_data,
                db=Mock()  # Mock database session
            )
            
            assert profile_response is not None
            assert "user_profile" in profile_response
            assert profile_response["user_profile"]["user_id"] == user_id
            
            # Simulate content strategy API call
            strategy_request = {
                "campaign_brief": "fitness studio promotion",
                "business_description": "Premium fitness studio",
                "target_audience_description": "Health-conscious professionals",
                "unique_value_proposition": "Results in 30 days"
            }
            
            with patch.object(service.content_generator, '_claude_generate_prompt', return_value="API test prompt"):
                with patch.object(service.content_generator, '_claude_generate_caption', return_value="API test caption"):
                    with patch.object(service.content_generator, '_claude_generate_hashtags', return_value=["#api", "#test"]):
                        
                        strategy_response = await service.get_personalized_image_strategy(
                            user_id=user_id,
                            campaign_brief=strategy_request["campaign_brief"],
                            business_description=strategy_request["business_description"],
                            target_audience_description=strategy_request["target_audience_description"],
                            unique_value_proposition=strategy_request["unique_value_proposition"]
                        )
            
            # Verify API response structure
            assert strategy_response is not None
            assert isinstance(strategy_response, dict)
            assert "content_variations" in strategy_response
            assert "ab_test_config" in strategy_response
            assert "personalization_insights" in strategy_response
    
    async def test_error_handling_in_content_generation(self, mock_user_profile_data):
        """Test error handling throughout content generation flow"""
        with patch('os.getenv', return_value=None):
            service = EnhancedPersonalizationService()
            
            # Test with invalid user ID
            with pytest.raises(ValueError):
                await service.get_personalized_image_strategy(
                    user_id="nonexistent_user",
                    campaign_brief="test campaign",
                    business_description="test business",
                    target_audience_description="test audience",
                    unique_value_proposition="test value"
                )
            
            # Create valid profile first
            user_id = "error_test_user"
            await service.personalization_engine.create_user_profile(
                user_id, mock_user_profile_data
            )
            
            # Test with content generation failure
            with patch.object(service.content_generator, 'generate_personalized_content_variations', side_effect=Exception("Content generation failed")):
                try:
                    await service.get_personalized_image_strategy(
                        user_id=user_id,
                        campaign_brief="test campaign",
                        business_description="test business",
                        target_audience_description="test audience",
                        unique_value_proposition="test value"
                    )
                    assert False, "Should have raised exception"
                except Exception as e:
                    assert "Content generation failed" in str(e)


@pytest.mark.integration 
class TestContentGenerationPerformance:
    """Test performance characteristics of content generation"""
    
    @pytest.mark.asyncio
    async def test_content_generation_performance(self, mock_user_profile_data):
        """Test content generation performance under normal load"""
        with patch('os.getenv', return_value=None):
            service = EnhancedPersonalizationService()
            
            # Create multiple user profiles
            user_ids = [f"perf_user_{i}" for i in range(10)]
            
            for user_id in user_ids:
                await service.personalization_engine.create_user_profile(
                    user_id, mock_user_profile_data
                )
            
            # Mock fast content generation
            with patch.object(service.content_generator, '_claude_generate_prompt', return_value="Performance test prompt"):
                with patch.object(service.content_generator, '_claude_generate_caption', return_value="Performance test caption"):
                    with patch.object(service.content_generator, '_claude_generate_hashtags', return_value=["#performance"]):
                        
                        import time
                        start_time = time.time()
                        
                        # Generate content for all users concurrently
                        tasks = []
                        for user_id in user_ids:
                            task = service.get_personalized_image_strategy(
                                user_id=user_id,
                                campaign_brief="performance test campaign",
                                business_description="test business",
                                target_audience_description="test audience",
                                unique_value_proposition="test value"
                            )
                            tasks.append(task)
                        
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        end_time = time.time()
                        total_time = end_time - start_time
                        
                        # Performance assertions
                        assert total_time < 5.0  # Should complete in under 5 seconds
                        assert len(results) == len(user_ids)
                        assert all(not isinstance(r, Exception) for r in results)


@pytest.mark.integration
class TestContentGenerationDataFlow:
    """Test data flow and transformations in content generation"""
    
    @pytest.mark.asyncio
    async def test_user_profile_to_content_transformation(self, mock_user_profile_data):
        """Test how user profile data transforms into content variations"""
        with patch('os.getenv', return_value=None):
            service = EnhancedPersonalizationService()
            
            user_id = "transform_test_user"
            
            # Create profile with specific characteristics
            profile_data = mock_user_profile_data.copy()
            profile_data.update({
                "industry": "restaurant",
                "brand_voice": "luxury",
                "target_age_groups": ["gen_x", "boomer"],
                "platform_priorities": ["facebook"]
            })
            
            profile = await service.personalization_engine.create_user_profile(
                user_id, profile_data
            )
            
            # Mock content generation to track transformations
            generated_prompts = []
            generated_captions = []
            generated_hashtags = []
            
            async def mock_prompt_gen(profile, brief, context):
                generated_prompts.append({"profile_industry": profile.industry, "context": context})
                return f"Luxury {profile.industry} content for {context.get('target_demographic', 'general')}"
            
            async def mock_caption_gen(profile, brief, context):
                generated_captions.append({"brand_voice": profile.brand_voice.value, "platform": context.get('platform')})
                return f"Elegant {brief} experience"
            
            async def mock_hashtag_gen(profile, brief, context, limit):
                hashtags = [f"#{profile.industry}", f"#{context.get('platform', 'social')}", "#luxury"]
                generated_hashtags.append(hashtags)
                return hashtags[:limit]
            
            with patch.object(service.content_generator, '_claude_generate_prompt', side_effect=mock_prompt_gen):
                with patch.object(service.content_generator, '_claude_generate_caption', side_effect=mock_caption_gen):
                    with patch.object(service.content_generator, '_claude_generate_hashtags', side_effect=mock_hashtag_gen):
                        
                        strategy = await service.get_personalized_image_strategy(
                            user_id=user_id,
                            campaign_brief="fine dining experience",
                            business_description="luxury restaurant",
                            target_audience_description="affluent diners",
                            unique_value_proposition="Michelin-starred cuisine"
                        )
            
            # Verify transformations occurred correctly
            assert len(generated_prompts) >= 3  # Control + variations
            assert any("restaurant" in prompt["profile_industry"] for prompt in generated_prompts)
            
            assert len(generated_captions) >= 3
            assert any(caption["brand_voice"] == "luxury" for caption in generated_captions)
            
            assert len(generated_hashtags) >= 3
            assert any("#restaurant" in tags for tags in generated_hashtags)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])