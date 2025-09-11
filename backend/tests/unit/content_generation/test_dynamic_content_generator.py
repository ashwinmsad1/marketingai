"""
Unit tests for Dynamic Content Generator
Tests core content generation functionality and Claude AI integration
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from ml.content_generation.dynamic_content_generator import (
    DynamicContentGenerator,
    ContentVariation, 
    AdaptiveContentSet
)
from engines.personalization_engine import (
    PersonalizationEngine,
    UserProfile,
    AgeGroup,
    BrandVoice,
    ContentPreference,
    PlatformPriority,
    CampaignObjective,
    BusinessSize,
    BudgetRange
)


@pytest.fixture
def mock_personalization_engine():
    """Mock personalization engine for testing"""
    engine = Mock(spec=PersonalizationEngine)
    engine.user_profiles = {}
    engine.platform_characteristics = {
        'instagram': {
            'optimal_formats': ['image'],
            'aspect_ratios': ['1:1'],
            'hashtag_limit': 30
        },
        'facebook': {
            'optimal_formats': ['image'],
            'aspect_ratios': ['16:9'],
            'hashtag_limit': 15
        },
        'facebook': {
            'optimal_formats': ['video'],
            'aspect_ratios': ['9:16'],
            'video_length_optimal': 8
        }
    }
    engine.demographic_insights = {
        'millennial': {
            'preferred_platforms': ['instagram', 'facebook']
        },
        'gen_z': {
            'preferred_platforms': ['facebook', 'instagram']
        }
    }
    return engine


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing"""
    return UserProfile(
        user_id="test_user_123",
        business_size=BusinessSize.SMB,
        industry="fitness",
        business_name="FitStudio Pro",
        budget_range=BudgetRange.SMALL,
        target_age_groups=[AgeGroup.MILLENNIAL, AgeGroup.GEN_Z],
        platform_priorities=[PlatformPriority.INSTAGRAM, PlatformPriority.FACEBOOK],
        brand_voice=BrandVoice.AUTHENTIC,
        content_preference=ContentPreference.MIXED,
        campaign_history=[],
        created_at=datetime.now()
    )


@pytest.fixture
def content_generator(mock_personalization_engine):
    """Content generator instance for testing"""
    with patch.dict('os.environ', {}, clear=True):
        generator = DynamicContentGenerator(mock_personalization_engine)
        # Mock Claude client to None for testing fallback methods
        generator.anthropic_client = None
        return generator


@pytest.fixture
def content_generator_with_claude(mock_personalization_engine):
    """Content generator with mocked Claude client"""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}, clear=True):
        generator = DynamicContentGenerator(mock_personalization_engine)
        # Mock the Claude client
        mock_client = Mock()
        generator.anthropic_client = mock_client
        return generator, mock_client


@pytest.mark.unit
@pytest.mark.asyncio
class TestDynamicContentGeneratorCore:
    """Test core functionality of Dynamic Content Generator"""
    
    async def test_initialization_without_api_key(self, mock_personalization_engine):
        """Test initialization without ANTHROPIC_API_KEY"""
        with patch.dict('os.environ', {}, clear=True):
            generator = DynamicContentGenerator(mock_personalization_engine)
            
            assert generator.personalization_engine == mock_personalization_engine
            assert generator.anthropic_client is None
            assert generator.performance_learnings == {}
    
    async def test_initialization_with_api_key(self, mock_personalization_engine):
        """Test initialization with ANTHROPIC_API_KEY"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}, clear=True):
            with patch('anthropic.Anthropic') as mock_anthropic:
                generator = DynamicContentGenerator(mock_personalization_engine)
                
                assert generator.personalization_engine == mock_personalization_engine
                mock_anthropic.assert_called_once_with(api_key='test-key')
    
    async def test_get_indian_market_context(self, content_generator):
        """Test Indian market context generation"""
        context = content_generator._get_indian_market_context()
        
        assert "Mobile-first audience" in context
        assert "UPI payment" in context
        assert "Price sensitivity" in context
        assert "WhatsApp and Instagram" in context
        assert "Regional diversity" in context
    
    async def test_get_style_preferences(self, content_generator):
        """Test style preference generation"""
        prefs = content_generator._get_style_preferences(
            BrandVoice.PROFESSIONAL, 
            "instagram"
        )
        
        assert prefs["tone"] == "professional"
        assert prefs["platform"] == "instagram"
        assert "clean, authoritative, trustworthy" in prefs["visual_style"]
        assert "Instagram-native" in prefs["platform_style"]


@pytest.mark.unit
@pytest.mark.asyncio
class TestContentVariationGeneration:
    """Test individual content variation generation methods"""
    
    async def test_generate_control_variation_fallback(self, content_generator, sample_user_profile):
        """Test control variation generation with fallback methods"""
        content_generator.personalization_engine.user_profiles["test_user_123"] = sample_user_profile
        
        variation = await content_generator._generate_control_variation(
            sample_user_profile,
            CampaignObjective.LEAD_GENERATION,
            "30-day fitness transformation program"
        )
        
        assert variation.variation_id == "control"
        assert variation.content_type == "image"
        assert "fitness" in variation.visual_prompt.lower()
        assert "transformation" in variation.visual_prompt.lower()
        assert len(variation.hashtags) >= 3
        assert variation.target_demographic == "general"
        assert variation.predicted_engagement > 0
        assert variation.predicted_ctr > 0
        assert variation.predicted_conversion > 0
    
    async def test_generate_demographic_variation_fallback(self, content_generator, sample_user_profile):
        """Test demographic variation generation with fallback"""
        variation = await content_generator._generate_demographic_variation(
            sample_user_profile,
            CampaignObjective.LEAD_GENERATION,
            "fitness program for professionals"
        )
        
        assert "demographic_millennial" in variation.variation_id
        assert variation.target_demographic == "millennial"
        assert variation.content_type in ["image", "video"]
        assert len(variation.hashtags) >= 2
        assert variation.predicted_engagement >= 3.0  # Demographic optimization boost
    
    async def test_generate_platform_variation(self, content_generator, sample_user_profile):
        """Test platform-optimized variation generation"""
        with patch.object(content_generator, '_claude_generate_prompt', return_value="Instagram-optimized fitness content"):
            with patch.object(content_generator, '_claude_generate_caption', return_value="Perfect for Instagram Stories! 💪"):
                with patch.object(content_generator, '_claude_generate_hashtags', return_value=["#fitness", "#instagram"]):
                    with patch.object(content_generator, '_claude_generate_color_palette', return_value=["#E1306C", "#405DE6"]):
                        
                        variation = await content_generator._generate_platform_variation(
                            sample_user_profile,
                            CampaignObjective.ENGAGEMENT,
                            "social media fitness content"
                        )
                        
                        assert "platform_instagram" in variation.variation_id
                        assert variation.platform_optimized == "instagram"
                        assert variation.visual_prompt == "Instagram-optimized fitness content"
                        assert variation.caption == "Perfect for Instagram Stories! 💪"
                        assert variation.hashtags == ["#fitness", "#instagram"]
                        assert variation.aspect_ratio == "1:1"  # Instagram optimal
    
    async def test_generate_performance_variation(self, content_generator, sample_user_profile):
        """Test performance-optimized variation generation"""
        # Add campaign history to profile
        sample_user_profile.campaign_history = [
            {"type": "video", "performance": {"roi": 15}},
            {"type": "image", "performance": {"roi": 12}}
        ]
        
        with patch.object(content_generator, '_claude_generate_prompt', return_value="Performance-optimized content"):
            with patch.object(content_generator, '_claude_generate_caption', return_value="Proven results! 🚀"):
                with patch.object(content_generator, '_claude_generate_hashtags', return_value=["#proven", "#results"]):
                    
                    variation = await content_generator._generate_performance_variation(
                        sample_user_profile,
                        CampaignObjective.SALES,
                        "high-converting fitness offer"
                    )
                    
                    assert variation.variation_id == "performance_optimized"
                    assert variation.target_demographic == "learned_audience"
                    assert variation.predicted_engagement > 2.5  # Performance boost applied
                    assert variation.content_type == "video"  # Best performing type


@pytest.mark.unit
@pytest.mark.asyncio
class TestClaudeAIIntegration:
    """Test Claude AI integration and fallback methods"""
    
    async def test_claude_generate_prompt_with_client(self, content_generator_with_claude, sample_user_profile):
        """Test Claude AI prompt generation with client"""
        generator, mock_client = content_generator_with_claude
        
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Professional fitness studio with modern equipment"
        
        with patch('asyncio.to_thread', return_value=mock_response):
            mock_client.messages.create.return_value = mock_response
            
            result = await generator._claude_generate_prompt(
                sample_user_profile,
                "fitness transformation",
                {"target_demographic": "millennial", "platform": "instagram"}
            )
            
            assert result == "Professional fitness studio with modern equipment"
            mock_client.messages.create.assert_called_once()
    
    async def test_claude_generate_caption_with_client(self, content_generator_with_claude, sample_user_profile):
        """Test Claude AI caption generation"""
        generator, mock_client = content_generator_with_claude
        
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Transform your fitness journey! 💪 Join us today! 🚀"
        
        with patch('asyncio.to_thread', return_value=mock_response):
            mock_client.messages.create.return_value = mock_response
            
            result = await generator._claude_generate_caption(
                sample_user_profile,
                "fitness program",
                {"platform": "instagram"}
            )
            
            assert "Transform your fitness journey!" in result
            assert "💪" in result
            assert "🚀" in result
    
    async def test_claude_generate_hashtags_with_client(self, content_generator_with_claude, sample_user_profile):
        """Test Claude AI hashtag generation"""
        generator, mock_client = content_generator_with_claude
        
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "#fitness, #transformation, #mumbai, #goals"
        
        with patch('asyncio.to_thread', return_value=mock_response):
            mock_client.messages.create.return_value = mock_response
            
            result = await generator._claude_generate_hashtags(
                sample_user_profile,
                "fitness program",
                {"platform": "instagram"},
                4
            )
            
            assert result == ["#fitness", "#transformation", "#mumbai", "#goals"]
    
    async def test_claude_generate_color_palette_with_client(self, content_generator_with_claude, sample_user_profile):
        """Test Claude AI color palette generation"""
        generator, mock_client = content_generator_with_claude
        
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "#FF5733, #33AFFF, #FFFFFF, #1E1E1E"
        
        with patch('asyncio.to_thread', return_value=mock_response):
            mock_client.messages.create.return_value = mock_response
            
            result = await generator._claude_generate_color_palette(
                sample_user_profile,
                {"platform": "instagram"}
            )
            
            assert result == ["#FF5733", "#33AFFF", "#FFFFFF", "#1E1E1E"]
            assert len(result) == 4
    
    async def test_fallback_methods_when_claude_fails(self, content_generator_with_claude, sample_user_profile):
        """Test fallback methods when Claude API fails"""
        generator, mock_client = content_generator_with_claude
        
        # Mock Claude API failure
        with patch('asyncio.to_thread', side_effect=Exception("API Error")):
            
            # Test prompt fallback
            prompt = await generator._claude_generate_prompt(
                sample_user_profile,
                "fitness content",
                {"platform": "instagram"}
            )
            assert "Professional fitness content" in prompt
            assert "mobile-first design" in prompt
            
            # Test caption fallback
            caption = await generator._claude_generate_caption(
                sample_user_profile,
                "fitness program",
                {"platform": "instagram"}
            )
            assert "fitness" in caption.lower()
            assert "#" in caption  # Should include hashtags
            
            # Test hashtag fallback
            hashtags = await generator._claude_generate_hashtags(
                sample_user_profile,
                "fitness content",
                {"platform": "instagram"},
                5
            )
            assert len(hashtags) <= 5
            assert all(tag.startswith("#") for tag in hashtags)
            
            # Test color palette fallback
            colors = await generator._claude_generate_color_palette(
                sample_user_profile,
                {"platform": "instagram"}
            )
            assert len(colors) == 4
            assert all(color.startswith("#") for color in colors)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAdaptiveContentSetGeneration:
    """Test complete content set generation"""
    
    async def test_generate_personalized_content_variations_success(self, content_generator, sample_user_profile):
        """Test successful content set generation"""
        content_generator.personalization_engine.user_profiles["test_user_123"] = sample_user_profile
        
        with patch.multiple(
            content_generator,
            _generate_control_variation=AsyncMock(return_value=Mock(spec=ContentVariation)),
            _generate_demographic_variation=AsyncMock(return_value=Mock(spec=ContentVariation)),
            _generate_platform_variation=AsyncMock(return_value=Mock(spec=ContentVariation)),
            _generate_performance_variation=AsyncMock(return_value=Mock(spec=ContentVariation))
        ):
            
            content_set = await content_generator.generate_personalized_content_variations(
                user_id="test_user_123",
                campaign_objective=CampaignObjective.LEAD_GENERATION,
                content_brief="fitness transformation program",
                num_variations=3
            )
            
            assert isinstance(content_set, AdaptiveContentSet)
            assert content_set.user_id == "test_user_123"
            assert content_set.campaign_objective == "lead_generation"
            assert len(content_set.variations) == 3
            assert content_set.control_variation is not None
            assert content_set.test_duration_days == 14
            assert content_set.primary_metric == "conversion_rate"
            assert "engagement_rate" in content_set.secondary_metrics
    
    async def test_generate_content_variations_user_not_found(self, content_generator):
        """Test error handling when user profile not found"""
        with pytest.raises(ValueError, match="User profile not found"):
            await content_generator.generate_personalized_content_variations(
                user_id="nonexistent_user",
                campaign_objective=CampaignObjective.ENGAGEMENT,
                content_brief="test campaign",
                num_variations=2
            )
    
    async def test_traffic_split_calculation(self, content_generator):
        """Test traffic split calculation for A/B testing"""
        split = content_generator._calculate_traffic_split(4)
        
        assert split["control"] == 0.4
        assert len(split) == 4
        assert sum(split.values()) == pytest.approx(1.0, abs=0.001)
    
    async def test_generate_test_hypothesis(self, content_generator, sample_user_profile):
        """Test A/B test hypothesis generation"""
        variations = [Mock(spec=ContentVariation) for _ in range(3)]
        
        hypothesis = content_generator._generate_test_hypothesis(sample_user_profile, variations)
        
        assert "Testing 3 personalized variations" in hypothesis
        assert "millennial" in hypothesis.lower()
        assert "instagram" in hypothesis.lower()
        assert "engagement by 15-25%" in hypothesis
        assert "conversion rate by 10-20%" in hypothesis
    
    async def test_get_primary_metric_mapping(self, content_generator):
        """Test primary metric mapping for different objectives"""
        assert content_generator._get_primary_metric(CampaignObjective.LEAD_GENERATION) == "conversion_rate"
        assert content_generator._get_primary_metric(CampaignObjective.BRAND_AWARENESS) == "engagement_rate"
        assert content_generator._get_primary_metric(CampaignObjective.SALES) == "conversion_rate"
        assert content_generator._get_primary_metric(CampaignObjective.ENGAGEMENT) == "engagement_rate"
        assert content_generator._get_primary_metric(CampaignObjective.TRAFFIC) == "ctr"


@pytest.mark.unit
@pytest.mark.asyncio
class TestUtilityMethods:
    """Test utility and helper methods"""
    
    async def test_get_optimal_content_type(self, content_generator, sample_user_profile):
        """Test optimal content type selection"""
        # Test video preference
        sample_user_profile.content_preference = ContentPreference.VIDEO_FIRST
        assert content_generator._get_optimal_content_type(sample_user_profile, CampaignObjective.ENGAGEMENT) == "video"
        
        # Test image preference
        sample_user_profile.content_preference = ContentPreference.IMAGE_HEAVY
        assert content_generator._get_optimal_content_type(sample_user_profile, CampaignObjective.ENGAGEMENT) == "image"
        
        # Test mixed preference
        sample_user_profile.content_preference = ContentPreference.MIXED
        assert content_generator._get_optimal_content_type(sample_user_profile, CampaignObjective.ENGAGEMENT) == "image"
    
    async def test_get_optimal_aspect_ratio(self, content_generator, sample_user_profile):
        """Test optimal aspect ratio selection"""
        # Test Facebook priority (landscape format)
        sample_user_profile.platform_priorities = [PlatformPriority.FACEBOOK]
        assert content_generator._get_optimal_aspect_ratio(sample_user_profile, CampaignObjective.ENGAGEMENT) == "16:9"
        
        # Test Instagram priority (default)
        sample_user_profile.platform_priorities = [PlatformPriority.INSTAGRAM]
        assert content_generator._get_optimal_aspect_ratio(sample_user_profile, CampaignObjective.ENGAGEMENT) == "1:1"
    
    async def test_demographic_optimal_methods(self, content_generator):
        """Test demographic-specific optimization methods"""
        # Test Gen Z preferences
        assert content_generator._get_demographic_optimal_content_type(AgeGroup.GEN_Z) == "video"
        assert content_generator._get_demographic_aspect_ratio(AgeGroup.GEN_Z) == "9:16"
        
        # Test Millennial preferences
        assert content_generator._get_demographic_optimal_content_type(AgeGroup.MILLENNIAL) == "image"
        assert content_generator._get_demographic_aspect_ratio(AgeGroup.MILLENNIAL) == "1:1"
        
        # Test preferred platform for demographic
        preferred = content_generator._get_demographic_preferred_platform(AgeGroup.MILLENNIAL)
        assert preferred == "instagram"  # Default fallback
    
    async def test_analyze_performance_history(self, content_generator, sample_user_profile):
        """Test performance history analysis"""
        # Test with no campaign history
        sample_user_profile.campaign_history = []
        analysis = content_generator._analyze_performance_history(sample_user_profile)
        assert analysis["performance_multiplier"] == 1.0
        assert analysis["best_content_type"] == "image"
        
        # Test with high-performing campaigns
        sample_user_profile.campaign_history = [
            {"type": "video", "performance": {"roi": 15}},
            {"type": "video", "performance": {"roi": 20}},
            {"type": "image", "performance": {"roi": 8}}
        ]
        analysis = content_generator._analyze_performance_history(sample_user_profile)
        assert analysis["performance_multiplier"] > 1.0
        assert analysis["best_content_type"] == "video"
        assert analysis["performance_multiplier"] <= 1.5  # Capped at 1.5x


@pytest.mark.unit
class TestDataStructures:
    """Test data structure validation and creation"""
    
    def test_content_variation_creation(self):
        """Test ContentVariation data structure"""
        variation = ContentVariation(
            variation_id="test_variation",
            content_type="image",
            visual_prompt="Test visual prompt",
            caption="Test caption",
            hashtags=["#test", "#variation"],
            visual_style="professional",
            color_palette=["#FF0000", "#00FF00"],
            aspect_ratio="1:1",
            target_demographic="millennial",
            platform_optimized="instagram",
            objective_focus="engagement",
            predicted_engagement=2.5,
            predicted_ctr=2.0,
            predicted_conversion=8.0
        )
        
        assert variation.variation_id == "test_variation"
        assert variation.content_type == "image"
        assert len(variation.hashtags) == 2
        assert len(variation.color_palette) == 2
        assert variation.predicted_engagement == 2.5
        assert isinstance(variation.created_at, datetime)
    
    def test_adaptive_content_set_creation(self):
        """Test AdaptiveContentSet data structure"""
        control_variation = Mock(spec=ContentVariation)
        test_variations = [Mock(spec=ContentVariation), Mock(spec=ContentVariation)]
        
        content_set = AdaptiveContentSet(
            content_set_id="test_set_123",
            user_id="user_456",
            campaign_objective="lead_generation",
            variations=test_variations,
            control_variation=control_variation,
            test_hypothesis="Test hypothesis",
            test_duration_days=14,
            traffic_split={"control": 0.4, "variation_1": 0.3, "variation_2": 0.3},
            primary_metric="conversion_rate",
            secondary_metrics=["engagement_rate", "ctr"]
        )
        
        assert content_set.content_set_id == "test_set_123"
        assert content_set.user_id == "user_456"
        assert len(content_set.variations) == 2
        assert content_set.test_duration_days == 14
        assert content_set.primary_metric == "conversion_rate"
        assert len(content_set.secondary_metrics) == 2
        assert isinstance(content_set.created_at, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])