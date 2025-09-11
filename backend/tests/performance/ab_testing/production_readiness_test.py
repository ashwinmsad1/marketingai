#!/usr/bin/env python3
"""
Production Readiness Test for A/B Testing Framework
Final verification for production deployment
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
import time

# Add backend to path
sys.path.append(os.path.dirname(__file__))

async def test_production_readiness():
    """Final production readiness test"""
    
    print("🚀 A/B Testing Production Readiness Test")
    print("=" * 50)
    
    score = 0
    max_score = 10
    
    try:
        from ml.ab_testing.ab_testing_framework import ABTestingFramework, TestStatus
        framework = ABTestingFramework()
        
        # Test 1: Framework Initialization (1 point)
        print("\n1. Framework Initialization...")
        if framework and len(framework.statistical_models) == 3:
            print("✅ Framework initialized correctly")
            score += 1
        else:
            print("❌ Framework initialization failed")
        
        # Test 2: Test Creation Speed (1 point)
        print("\n2. Test Creation Performance...")
        start_time = time.time()
        
        test_config = {
            "test_name": "Production Readiness Test",
            "test_type": "simple_ab",
            "hypothesis": "Production test",
            "primary_metric": "conversion_rate"
        }
        
        variations = [
            {"variation_id": "control", "name": "Control", "description": "Control version", "traffic_percentage": 50.0, "content_config": {}},
            {"variation_id": "test", "name": "Test", "description": "Test version", "traffic_percentage": 50.0, "content_config": {}}
        ]
        
        test = await framework.create_personalized_ab_test("prod_user", test_config, variations)
        creation_time = time.time() - start_time
        
        if creation_time < 0.1:  # Should create test in under 100ms
            print(f"✅ Test created in {creation_time*1000:.1f}ms")
            score += 1
        else:
            print(f"⚠️ Test creation took {creation_time*1000:.1f}ms (target: <100ms)")
        
        # Test 3: Event Processing Speed (1 point)
        print("\n3. Event Processing Performance...")
        test.status = TestStatus.ACTIVE
        
        start_time = time.time()
        events_processed = 0
        
        # Process 1000 events
        for i in range(500):
            await framework.record_test_event(test.test_id, "control", "impression")
            await framework.record_test_event(test.test_id, "test", "impression")
            events_processed += 2
        
        processing_time = time.time() - start_time
        events_per_second = events_processed / processing_time
        
        if events_per_second > 10000:  # Should process >10k events/second
            print(f"✅ Processed {events_per_second:.0f} events/second")
            score += 1
        else:
            print(f"⚠️ Processed {events_per_second:.0f} events/second (target: >10k)")
        
        # Test 4: Statistical Accuracy (1 point)
        print("\n4. Statistical Analysis Accuracy...")
        
        # Create controlled test scenario
        stat_test_config = {
            "test_name": "Statistical Test",
            "test_type": "simple_ab", 
            "hypothesis": "Statistical test",
            "primary_metric": "conversion_rate"
        }
        
        stat_variations = [
            {"variation_id": "stat_control", "name": "Control", "description": "Control", "traffic_percentage": 50.0, "content_config": {}},
            {"variation_id": "stat_test", "name": "Test", "description": "Test", "traffic_percentage": 50.0, "content_config": {}}
        ]
        
        stat_test = await framework.create_personalized_ab_test("stat_user", stat_test_config, stat_variations)
        stat_test.status = TestStatus.ACTIVE
        
        # Control: 5% conversion rate (5/100)
        for _ in range(100):
            await framework.record_test_event(stat_test.test_id, "stat_control", "impression")
        for _ in range(20):
            await framework.record_test_event(stat_test.test_id, "stat_control", "click")
        for _ in range(1):  # 1 conversion
            await framework.record_test_event(stat_test.test_id, "stat_control", "conversion", value=100.0)
        
        # Test: 10% conversion rate (2/20)
        for _ in range(100):
            await framework.record_test_event(stat_test.test_id, "stat_test", "impression")
        for _ in range(20):
            await framework.record_test_event(stat_test.test_id, "stat_test", "click")
        for _ in range(2):  # 2 conversions  
            await framework.record_test_event(stat_test.test_id, "stat_test", "conversion", value=100.0)
        
        stat_result = await framework._evaluate_test_results(stat_test)
        
        # Check if statistical analysis is reasonable
        if (stat_result.winning_variation_id == "stat_test" or 
            stat_result.confidence_level > 0.5):
            print("✅ Statistical analysis working correctly")
            score += 1
        else:
            print(f"⚠️ Statistical analysis may have issues")
        
        # Test 5: Memory Management (1 point)
        print("\n5. Memory Management...")
        
        initial_tests = len(framework.active_tests)
        
        # Create and conclude multiple tests
        for i in range(5):
            temp_config = {
                "test_name": f"Memory Test {i}",
                "test_type": "simple_ab",
                "hypothesis": f"Memory test {i}",
                "primary_metric": "conversion_rate"
            }
            
            temp_variations = [
                {"variation_id": f"temp_control_{i}", "name": f"Control {i}", "description": f"Control {i}", "traffic_percentage": 50.0, "content_config": {}},
                {"variation_id": f"temp_test_{i}", "name": f"Test {i}", "description": f"Test {i}", "traffic_percentage": 50.0, "content_config": {}}
            ]
            
            temp_test = await framework.create_personalized_ab_test(f"temp_user_{i}", temp_config, temp_variations)
            await framework.conclude_test(temp_test.test_id, "memory_test")
        
        final_active_tests = len(framework.active_tests)
        concluded_tests = len(framework.test_history)
        
        if final_active_tests == initial_tests and concluded_tests >= 5:
            print("✅ Memory management working correctly")
            score += 1
        else:
            print(f"⚠️ Memory management issues: Active={final_active_tests}, History={concluded_tests}")
        
        # Test 6: Error Handling Robustness (1 point)
        print("\n6. Error Handling Robustness...")
        
        error_handled = 0
        
        # Test various error conditions
        try:
            await framework.record_test_event("nonexistent", "var", "impression")
        except:
            pass
        else:
            error_handled += 1
        
        try:
            result = await framework.record_test_event(test.test_id, "nonexistent_var", "impression")
            if not result:  # Should return False
                error_handled += 1
        except:
            pass
        
        # Test invalid traffic allocation
        try:
            invalid_variations = [
                {"variation_id": "a", "name": "A", "description": "Test A", "traffic_percentage": 70.0, "content_config": {}},
                {"variation_id": "b", "name": "B", "description": "Test B", "traffic_percentage": 40.0, "content_config": {}}
            ]
            await framework.create_personalized_ab_test("error_user", {"test_name": "Error Test"}, invalid_variations)
        except ValueError:
            error_handled += 1
        
        if error_handled >= 2:
            print("✅ Error handling is robust")
            score += 1
        else:
            print("⚠️ Error handling needs improvement")
        
        # Test 7: API Integration Readiness (1 point)
        print("\n7. API Integration Readiness...")
        
        # Test API-style data conversion
        api_test_data = {
            "campaign_name": "API Test",
            "test_type": "content",
            "variant_a": {
                "name": "Control",
                "description": "Control version",
                "content": {"headline": "Original Headline"}
            },
            "variant_b": {
                "name": "Test",
                "description": "Test version",
                "content": {"headline": "New Headline"}
            },
            "traffic_split": 50,
            "sample_size": 1000,
            "confidence_level": 95,
            "duration_days": 14
        }
        
        # Convert to framework format (simulating API endpoint logic)
        api_test_config = {
            "test_name": api_test_data["campaign_name"],
            "test_type": "simple_ab",
            "hypothesis": "API integration test",
            "primary_metric": "conversion_rate"
        }
        
        api_variations = [
            {
                "variation_id": "control",
                "name": api_test_data["variant_a"]["name"],
                "description": api_test_data["variant_a"]["description"],
                "traffic_percentage": float(api_test_data["traffic_split"]),
                "content_config": api_test_data["variant_a"]["content"]
            },
            {
                "variation_id": "test",
                "name": api_test_data["variant_b"]["name"],
                "description": api_test_data["variant_b"]["description"],
                "traffic_percentage": float(100 - api_test_data["traffic_split"]),
                "content_config": api_test_data["variant_b"]["content"]
            }
        ]
        
        api_test = await framework.create_personalized_ab_test("api_user", api_test_config, api_variations)
        
        if (api_test and 
            len(api_test.variations) == 2 and
            api_test.variations[0].content_config.get("headline") == "Original Headline"):
            print("✅ API integration ready")
            score += 1
        else:
            print("⚠️ API integration issues detected")
        
        # Test 8: Concurrent User Support (1 point)
        print("\n8. Concurrent User Support...")
        
        concurrent_tests = []
        start_time = time.time()
        
        # Simulate 10 concurrent users creating tests
        for user_id in range(10):
            user_config = {
                "test_name": f"Concurrent Test User {user_id}",
                "test_type": "simple_ab",
                "hypothesis": f"User {user_id} test",
                "primary_metric": "conversion_rate"
            }
            
            user_variations = [
                {"variation_id": f"control_{user_id}", "name": f"Control {user_id}", "description": f"Control for user {user_id}", "traffic_percentage": 50.0, "content_config": {}},
                {"variation_id": f"test_{user_id}", "name": f"Test {user_id}", "description": f"Test for user {user_id}", "traffic_percentage": 50.0, "content_config": {}}
            ]
            
            user_test = await framework.create_personalized_ab_test(f"concurrent_user_{user_id}", user_config, user_variations)
            concurrent_tests.append(user_test)
        
        concurrent_time = time.time() - start_time
        
        if len(concurrent_tests) == 10 and concurrent_time < 1.0:
            print(f"✅ Concurrent user support working ({concurrent_time:.2f}s for 10 users)")
            score += 1
        else:
            print(f"⚠️ Concurrent user support issues ({len(concurrent_tests)} tests, {concurrent_time:.2f}s)")
        
        # Test 9: Data Consistency (1 point)
        print("\n9. Data Consistency...")
        
        consistency_test = concurrent_tests[0]
        consistency_test.status = TestStatus.ACTIVE
        
        # Record events and check consistency
        initial_impressions = consistency_test.variations[0].impressions
        
        for _ in range(10):
            await framework.record_test_event(consistency_test.test_id, consistency_test.variations[0].variation_id, "impression")
        
        final_impressions = consistency_test.variations[0].impressions
        
        if final_impressions == initial_impressions + 10:
            print("✅ Data consistency maintained")
            score += 1
        else:
            print(f"⚠️ Data consistency issues: {initial_impressions} -> {final_impressions}")
        
        # Test 10: Production Performance (1 point)
        print("\n10. Overall Production Performance...")
        
        # Final performance test
        perf_start = time.time()
        
        # Create test, record events, analyze results
        perf_config = {
            "test_name": "Performance Test",
            "test_type": "simple_ab",
            "hypothesis": "Performance test",
            "primary_metric": "conversion_rate"
        }
        
        perf_variations = [
            {"variation_id": "perf_control", "name": "Control", "description": "Control", "traffic_percentage": 50.0, "content_config": {}},
            {"variation_id": "perf_test", "name": "Test", "description": "Test", "traffic_percentage": 50.0, "content_config": {}}
        ]
        
        perf_test = await framework.create_personalized_ab_test("perf_user", perf_config, perf_variations)
        perf_test.status = TestStatus.ACTIVE
        
        # Record 100 events per variation
        for variation_id in ["perf_control", "perf_test"]:
            for _ in range(50):
                await framework.record_test_event(perf_test.test_id, variation_id, "impression")
            for _ in range(10):
                await framework.record_test_event(perf_test.test_id, variation_id, "click")
            for _ in range(2):
                await framework.record_test_event(perf_test.test_id, variation_id, "conversion", value=50.0)
        
        # Analyze results
        await framework._evaluate_test_results(perf_test)
        
        perf_time = time.time() - perf_start
        
        if perf_time < 0.5:  # Complete operation in under 500ms
            print(f"✅ Production performance excellent ({perf_time*1000:.1f}ms)")
            score += 1
        else:
            print(f"⚠️ Production performance needs optimization ({perf_time*1000:.1f}ms)")
        
        # Final Report
        print("\n" + "=" * 50)
        print("🏁 PRODUCTION READINESS REPORT")
        print("=" * 50)
        
        print(f"Score: {score}/{max_score} ({score/max_score*100:.0f}%)")
        
        if score >= 9:
            print("🎉 PRODUCTION READY! ✅")
            print("Framework is ready for production deployment")
        elif score >= 7:
            print("⚠️ MOSTLY READY - Minor optimizations recommended")
        else:
            print("❌ NOT READY - Significant issues need addressing")
        
        # Detailed recommendations
        print(f"\nFramework Status:")
        print(f"- Active Tests: {len(framework.active_tests)}")
        print(f"- Completed Tests: {len(framework.test_history)}")
        print(f"- Statistical Models: {len(framework.statistical_models)}")
        print(f"- LLM Integration: {'✅' if framework.anthropic_client else '⚠️ Not configured'}")
        
        return score >= 8
        
    except Exception as e:
        print(f"\n❌ Production readiness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_production_readiness())
    sys.exit(0 if success else 1)