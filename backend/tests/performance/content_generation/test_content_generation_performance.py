"""
Performance tests for Dynamic Content Generator
Tests scalability, response times, and resource usage under load
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from ml.content_generation.dynamic_content_generator import DynamicContentGenerator
from engines.personalization_engine import (
    PersonalizationEngine, 
    UserProfile,
    AgeGroup,
    BrandVoice,
    CampaignObjective,
    BusinessSize,
    BudgetRange,
    ContentPreference,
    PlatformPriority
)


@pytest.fixture
def mock_personalization_engine():
    """Mock personalization engine for performance testing"""
    engine = Mock(spec=PersonalizationEngine)
    engine.user_profiles = {}
    engine.platform_characteristics = {
        'instagram': {'optimal_formats': ['image'], 'aspect_ratios': ['1:1']},
        'facebook': {'optimal_formats': ['image'], 'aspect_ratios': ['16:9']},
        'instagram': {'optimal_formats': ['video'], 'aspect_ratios': ['9:16']}
    }
    engine.demographic_insights = {
        'millennial': {'preferred_platforms': ['instagram']},
        'gen_z': {'preferred_platforms': ['facebook', 'instagram']}
    }
    return engine


@pytest.fixture
def performance_user_profiles():
    """Generate multiple user profiles for performance testing"""
    profiles = []
    industries = ["fitness", "restaurant", "tech", "fashion", "education"]
    brand_voices = [BrandVoice.PROFESSIONAL, BrandVoice.CASUAL, BrandVoice.LUXURY]
    age_groups = [AgeGroup.GEN_Z, AgeGroup.MILLENNIAL, AgeGroup.GEN_X]
    
    for i in range(50):
        profile = UserProfile(
            user_id=f"perf_user_{i}",
            business_size=BusinessSize.SMB,
            industry=industries[i % len(industries)],
            business_name=f"Test Business {i}",
            budget_range=BudgetRange.MEDIUM,
            target_age_groups=[age_groups[i % len(age_groups)]],
            platform_priorities=[PlatformPriority.INSTAGRAM, PlatformPriority.FACEBOOK],
            brand_voice=brand_voices[i % len(brand_voices)],
            content_preference=ContentPreference.MIXED,
            campaign_history=[]
        )
        profiles.append(profile)
    
    return profiles


@pytest.mark.performance
@pytest.mark.asyncio
class TestContentGenerationPerformance:
    """Test performance characteristics of content generation"""
    
    async def test_single_content_generation_response_time(self, mock_personalization_engine, performance_user_profiles):
        """Test response time for single content generation request"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None  # Use fallback methods for consistent timing
        
        profile = performance_user_profiles[0]
        mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        # Measure response time
        start_time = time.time()
        
        content_set = await content_generator.generate_personalized_content_variations(
            user_id=profile.user_id,
            campaign_objective=CampaignObjective.LEAD_GENERATION,
            content_brief="fitness studio promotion",
            num_variations=3
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"Single content generation time: {response_time:.3f}s")
        
        # Performance assertions
        assert response_time < 2.0  # Should complete in under 2 seconds
        assert content_set is not None
        assert len(content_set.variations) == 3
    
    async def test_batch_content_generation_throughput(self, mock_personalization_engine, performance_user_profiles):
        """Test throughput when generating content for multiple users"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        # Setup profiles in mock engine
        for profile in performance_user_profiles[:20]:  # Test with 20 users
            mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        start_time = time.time()
        
        # Generate content for all users concurrently
        tasks = []
        for i, profile in enumerate(performance_user_profiles[:20]):
            task = content_generator.generate_personalized_content_variations(
                user_id=profile.user_id,
                campaign_objective=CampaignObjective.ENGAGEMENT,
                content_brief=f"campaign {i}",
                num_variations=2
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        throughput = len(results) / total_time
        
        print(f"Batch generation: {len(results)} content sets in {total_time:.3f}s")
        print(f"Throughput: {throughput:.2f} generations/second")
        
        # Performance assertions
        assert total_time < 10.0  # 20 generations should complete in under 10 seconds
        assert throughput > 2.0  # Should achieve >2 generations/second
        assert len(results) == 20
        assert all(result is not None for result in results)
    
    async def test_content_generation_scalability(self, mock_personalization_engine, performance_user_profiles):
        """Test how performance scales with increasing load"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        # Setup all profiles
        for profile in performance_user_profiles:
            mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        load_scenarios = [1, 5, 10, 20, 30]
        performance_results = []
        
        for load in load_scenarios:
            start_time = time.time()
            
            tasks = []
            for i in range(load):
                profile = performance_user_profiles[i]
                task = content_generator.generate_personalized_content_variations(
                    user_id=profile.user_id,
                    campaign_objective=CampaignObjective.SALES,
                    content_brief=f"scalability test {i}",
                    num_variations=2
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time_per_request = total_time / load
            
            performance_results.append({
                "load": load,
                "total_time": total_time,
                "avg_time_per_request": avg_time_per_request,
                "throughput": load / total_time
            })
            
            print(f"Load {load}: {total_time:.3f}s total, {avg_time_per_request:.3f}s avg, {load/total_time:.2f} req/s")
        
        # Scalability assertions
        for result in performance_results:
            assert result["avg_time_per_request"] < 5.0  # Average should stay under 5s
            assert result["throughput"] > 0.5  # Should maintain >0.5 req/s throughput
        
        # Performance should not degrade linearly (should benefit from async)
        low_load_avg = performance_results[0]["avg_time_per_request"]
        high_load_avg = performance_results[-1]["avg_time_per_request"]
        degradation_factor = high_load_avg / low_load_avg
        
        assert degradation_factor < 10  # Performance should not degrade >10x
    
    async def test_claude_api_fallback_performance(self, mock_personalization_engine, performance_user_profiles):
        """Test performance when Claude API is unavailable and fallbacks are used"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None  # Force fallback mode
        
        profile = performance_user_profiles[0]
        mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        # Test fallback methods performance
        fallback_tests = [
            ("prompt_generation", content_generator._claude_generate_prompt),
            ("caption_generation", content_generator._claude_generate_caption),
            ("hashtag_generation", lambda p, b, c: content_generator._claude_generate_hashtags(p, b, c, 10)),
            ("color_palette_generation", content_generator._claude_generate_color_palette)
        ]
        
        for test_name, method in fallback_tests:
            start_time = time.time()
            
            # Run fallback method multiple times
            for _ in range(10):
                result = await method(
                    profile,
                    "test campaign brief",
                    {"platform": "instagram", "target_demographic": "millennial"}
                )
                assert result is not None
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 10
            
            print(f"Fallback {test_name}: {avg_time*1000:.2f}ms average")
            
            # Fallback methods should be very fast
            assert avg_time < 0.1  # Should be under 100ms per call
    
    async def test_memory_usage_under_sustained_load(self, mock_personalization_engine, performance_user_profiles):
        """Test memory usage patterns under sustained content generation load"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_monitoring = True
        except ImportError:
            print("psutil not available - skipping memory monitoring")
            memory_monitoring = False
            initial_memory = 0
        
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        # Setup profiles
        for profile in performance_user_profiles[:30]:
            mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        # Run sustained load test
        cycles = 5
        requests_per_cycle = 6
        
        for cycle in range(cycles):
            # Generate content in batches
            tasks = []
            for i in range(requests_per_cycle):
                profile_idx = (cycle * requests_per_cycle + i) % len(performance_user_profiles[:30])
                profile = performance_user_profiles[profile_idx]
                
                task = content_generator.generate_personalized_content_variations(
                    user_id=profile.user_id,
                    campaign_objective=CampaignObjective.ENGAGEMENT,
                    content_brief=f"memory test cycle {cycle} request {i}",
                    num_variations=3
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            assert len(results) == requests_per_cycle
            
            if memory_monitoring:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                print(f"Cycle {cycle}: Memory usage: {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
        
        if memory_monitoring:
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            total_memory_increase = final_memory - initial_memory
            print(f"Total memory increase: {total_memory_increase:.1f}MB")
            
            # Memory should not increase excessively
            assert total_memory_increase < 50  # Should not increase by more than 50MB
        
        print(f"Completed {cycles * requests_per_cycle} content generations successfully")
    
    async def test_concurrent_user_content_generation(self, mock_personalization_engine, performance_user_profiles):
        """Test performance with multiple concurrent users generating content"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        # Setup profiles
        test_profiles = performance_user_profiles[:15]
        for profile in test_profiles:
            mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        start_time = time.time()
        
        # Simulate concurrent users each making multiple requests
        all_tasks = []
        
        for profile in test_profiles:
            # Each user makes 3 different content requests
            for request_num in range(3):
                task = content_generator.generate_personalized_content_variations(
                    user_id=profile.user_id,
                    campaign_objective=CampaignObjective.LEAD_GENERATION,
                    content_brief=f"{profile.industry} campaign {request_num}",
                    num_variations=2
                )
                all_tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*all_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        total_requests = len(all_tasks)
        requests_per_second = total_requests / total_time
        
        print(f"Concurrent test: {total_requests} requests from {len(test_profiles)} users")
        print(f"Total time: {total_time:.3f}s")
        print(f"Throughput: {requests_per_second:.2f} requests/second")
        
        # Performance assertions
        assert total_time < 15.0  # Should handle all requests in under 15 seconds
        assert requests_per_second > 3.0  # Should maintain >3 requests/second
        assert len(results) == total_requests
        assert all(result is not None for result in results)
        
        # Verify content quality wasn't compromised
        for result in results[:5]:  # Spot check first 5 results
            assert len(result.variations) == 2
            assert result.control_variation is not None
            assert all(len(v.hashtags) > 0 for v in result.variations)


@pytest.mark.performance
class TestContentGenerationResourceUsage:
    """Test resource usage patterns of content generation"""
    
    @pytest.mark.asyncio
    async def test_cpu_intensive_operations_performance(self, mock_personalization_engine, performance_user_profiles):
        """Test performance of CPU-intensive operations like statistical analysis"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        # Create profile with extensive campaign history for analysis
        profile = performance_user_profiles[0]
        profile.campaign_history = [
            {"type": "image", "performance": {"roi": 10 + i, "ctr": 2.0 + (i * 0.1)}}
            for i in range(100)  # 100 historical campaigns
        ]
        mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        start_time = time.time()
        
        # Test performance analysis intensive operation
        for _ in range(10):
            analysis = content_generator._analyze_performance_history(profile)
            assert analysis["performance_multiplier"] > 1.0
        
        end_time = time.time()
        avg_analysis_time = (end_time - start_time) / 10
        
        print(f"Performance analysis time: {avg_analysis_time*1000:.2f}ms per analysis")
        
        # Should handle large campaign histories efficiently
        assert avg_analysis_time < 0.05  # Should be under 50ms per analysis
    
    def test_content_generation_thread_safety(self, mock_personalization_engine, performance_user_profiles):
        """Test thread safety of content generation operations"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        # Setup profiles
        test_profiles = performance_user_profiles[:10]
        for profile in test_profiles:
            mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        def generate_content_sync(profile):
            """Synchronous wrapper for thread testing"""
            return asyncio.run(
                content_generator.generate_personalized_content_variations(
                    user_id=profile.user_id,
                    campaign_objective=CampaignObjective.ENGAGEMENT,
                    content_brief=f"thread test for {profile.business_name}",
                    num_variations=2
                )
            )
        
        # Run content generation from multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            
            futures = [
                executor.submit(generate_content_sync, profile)
                for profile in test_profiles
            ]
            
            results = [future.result() for future in futures]
            
            end_time = time.time()
            total_time = end_time - start_time
        
        print(f"Thread safety test: {len(results)} generations in {total_time:.3f}s")
        
        # All operations should complete successfully
        assert len(results) == len(test_profiles)
        assert all(result is not None for result in results)
        assert total_time < 10.0  # Should complete in reasonable time


@pytest.mark.performance
class TestContentGenerationOptimization:
    """Test optimization features and performance improvements"""
    
    @pytest.mark.asyncio
    async def test_caching_performance_improvement(self, mock_personalization_engine, performance_user_profiles):
        """Test performance improvements from caching user contexts"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        profile = performance_user_profiles[0]
        mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        # Test without caching (first run)
        start_time = time.time()
        
        result1 = await content_generator.generate_personalized_content_variations(
            user_id=profile.user_id,
            campaign_objective=CampaignObjective.SALES,
            content_brief="caching test campaign",
            num_variations=3
        )
        
        first_run_time = time.time() - start_time
        
        # Test with potential caching benefits (second run - same user/brief)
        start_time = time.time()
        
        result2 = await content_generator.generate_personalized_content_variations(
            user_id=profile.user_id,
            campaign_objective=CampaignObjective.SALES,
            content_brief="caching test campaign",
            num_variations=3
        )
        
        second_run_time = time.time() - start_time
        
        print(f"First run: {first_run_time:.3f}s, Second run: {second_run_time:.3f}s")
        
        # Both should complete successfully
        assert result1 is not None
        assert result2 is not None
        assert len(result1.variations) == 3
        assert len(result2.variations) == 3
        
        # Performance should be consistent (testing that there are no major slowdowns)
        assert abs(first_run_time - second_run_time) < first_run_time * 0.5  # Within 50% variance
    
    @pytest.mark.asyncio
    async def test_batch_optimization_performance(self, mock_personalization_engine, performance_user_profiles):
        """Test performance optimizations for batch operations"""
        content_generator = DynamicContentGenerator(mock_personalization_engine)
        content_generator.anthropic_client = None
        
        # Setup profiles
        batch_profiles = performance_user_profiles[:8]
        for profile in batch_profiles:
            mock_personalization_engine.user_profiles[profile.user_id] = profile
        
        # Test individual requests
        start_time = time.time()
        
        individual_results = []
        for profile in batch_profiles:
            result = await content_generator.generate_personalized_content_variations(
                user_id=profile.user_id,
                campaign_objective=CampaignObjective.ENGAGEMENT,
                content_brief="individual test",
                num_variations=2
            )
            individual_results.append(result)
        
        individual_time = time.time() - start_time
        
        # Test batch concurrent requests
        start_time = time.time()
        
        batch_tasks = []
        for profile in batch_profiles:
            task = content_generator.generate_personalized_content_variations(
                user_id=profile.user_id,
                campaign_objective=CampaignObjective.ENGAGEMENT,
                content_brief="batch test",
                num_variations=2
            )
            batch_tasks.append(task)
        
        batch_results = await asyncio.gather(*batch_tasks)
        batch_time = time.time() - start_time
        
        print(f"Individual: {individual_time:.3f}s, Batch: {batch_time:.3f}s")
        print(f"Batch speedup: {individual_time / batch_time:.2f}x")
        
        # Batch should be faster due to concurrency
        assert batch_time < individual_time
        assert len(batch_results) == len(individual_results)
        
        # Significant performance improvement expected
        speedup = individual_time / batch_time
        assert speedup > 1.5  # Should be at least 1.5x faster


if __name__ == "__main__":
    pytest.main([__file__, "-v"])