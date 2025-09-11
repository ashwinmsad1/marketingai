"""
Performance and load tests for A/B Testing Framework
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

from ml.ab_testing.ab_testing_framework import ABTestingFramework, TestStatus


@pytest.mark.performance
@pytest.mark.asyncio
class TestABTestingPerformance:
    """Test A/B testing framework performance under load."""
    
    async def test_test_creation_performance(self, ab_framework):
        """Test performance of creating multiple A/B tests."""
        test_configs = []
        for i in range(50):  # Create 50 tests
            test_configs.append({
                "test_name": f"Performance Test {i}",
                "test_type": "simple_ab",
                "hypothesis": f"Performance test {i}",
                "primary_metric": "conversion_rate"
            })
        
        variations_template = [
            {
                "variation_id": "control",
                "name": "Control",
                "description": "Control version",
                "traffic_percentage": 50.0,
                "content_config": {"type": "control"}
            },
            {
                "variation_id": "test",
                "name": "Test",
                "description": "Test version",
                "traffic_percentage": 50.0,
                "content_config": {"type": "test"}
            }
        ]
        
        start_time = time.time()
        
        tests = []
        for i, config in enumerate(test_configs):
            test = await ab_framework.create_personalized_ab_test(
                f"perf_user_{i}", config, variations_template
            )
            tests.append(test)
        
        creation_time = time.time() - start_time
        avg_time_per_test = creation_time / len(test_configs)
        
        print(f"Created {len(tests)} tests in {creation_time:.3f}s")
        print(f"Average time per test: {avg_time_per_test*1000:.2f}ms")
        
        # Performance assertions
        assert len(tests) == 50
        assert creation_time < 5.0  # Should create 50 tests in under 5 seconds
        assert avg_time_per_test < 0.1  # Each test should take less than 100ms
    
    async def test_event_processing_throughput(self, ab_framework, active_test):
        """Test event processing throughput."""
        num_events = 10000
        event_types = ["impression", "click", "conversion"]
        
        start_time = time.time()
        
        # Process events in batches for realism
        for i in range(num_events):
            event_type = event_types[i % len(event_types)]
            variation_id = "control" if i % 2 == 0 else "test"
            
            await ab_framework.record_test_event(
                active_test.test_id, variation_id, event_type, value=50.0
            )
        
        processing_time = time.time() - start_time
        events_per_second = num_events / processing_time
        
        print(f"Processed {num_events} events in {processing_time:.3f}s")
        print(f"Throughput: {events_per_second:.0f} events/second")
        
        # Performance assertions
        assert events_per_second > 5000  # Should process >5k events/second
        assert processing_time < 10.0  # Should process 10k events in under 10s
        
        # Verify data integrity
        total_events = sum(v.impressions + v.clicks + v.conversions for v in active_test.variations)
        assert total_events == num_events
    
    async def test_concurrent_test_management(self, ab_framework):
        """Test managing multiple concurrent tests."""
        num_concurrent_tests = 20
        
        # Create concurrent tests
        test_creation_start = time.time()
        
        tasks = []
        for i in range(num_concurrent_tests):
            config = {
                "test_name": f"Concurrent Test {i}",
                "test_type": "simple_ab",
                "hypothesis": f"Concurrent test {i}",
                "primary_metric": "conversion_rate"
            }
            
            variations = [
                {
                    "variation_id": f"control_{i}",
                    "name": f"Control {i}",
                    "description": f"Control for test {i}",
                    "traffic_percentage": 50.0,
                    "content_config": {"test_id": i}
                },
                {
                    "variation_id": f"test_{i}",
                    "name": f"Test {i}",
                    "description": f"Test for test {i}",
                    "traffic_percentage": 50.0,
                    "content_config": {"test_id": i}
                }
            ]
            
            task = ab_framework.create_personalized_ab_test(
                f"concurrent_user_{i}", config, variations
            )
            tasks.append(task)
        
        tests = await asyncio.gather(*tasks)
        creation_time = time.time() - test_creation_start
        
        print(f"Created {len(tests)} concurrent tests in {creation_time:.3f}s")
        
        # Activate all tests
        for test in tests:
            test.status = TestStatus.ACTIVE
        
        # Record events concurrently
        event_recording_start = time.time()
        
        event_tasks = []
        for i, test in enumerate(tests):
            # Create event recording tasks for each test
            for j in range(100):  # 100 events per test
                event_type = ["impression", "click", "conversion"][j % 3]
                variation_id = f"control_{i}" if j % 2 == 0 else f"test_{i}"
                
                task = ab_framework.record_test_event(
                    test.test_id, variation_id, event_type, value=25.0
                )
                event_tasks.append(task)
        
        # Execute all event recording tasks concurrently
        await asyncio.gather(*event_tasks)
        event_recording_time = time.time() - event_recording_start
        
        total_events = len(event_tasks)
        events_per_second = total_events / event_recording_time
        
        print(f"Recorded {total_events} events across {len(tests)} tests in {event_recording_time:.3f}s")
        print(f"Concurrent event throughput: {events_per_second:.0f} events/second")
        
        # Performance assertions
        assert len(tests) == num_concurrent_tests
        assert creation_time < 2.0  # Should create 20 tests in under 2 seconds
        assert events_per_second > 1000  # Should handle >1k events/second concurrently
        
        # Verify framework state
        assert len(ab_framework.active_tests) == num_concurrent_tests
    
    async def test_statistical_analysis_performance(self, ab_framework):
        """Test performance of statistical analysis on large datasets."""
        # Create test with substantial data
        test_config = {
            "test_name": "Statistical Performance Test",
            "test_type": "simple_ab",
            "hypothesis": "Statistical analysis performance test",
            "primary_metric": "conversion_rate"
        }
        
        variations = [
            {
                "variation_id": "control",
                "name": "Control",
                "description": "Control with large dataset",
                "traffic_percentage": 50.0,
                "content_config": {"dataset": "large"}
            },
            {
                "variation_id": "test",
                "name": "Test",
                "description": "Test with large dataset",
                "traffic_percentage": 50.0,
                "content_config": {"dataset": "large"}
            }
        ]
        
        test = await ab_framework.create_personalized_ab_test("stats_user", test_config, variations)
        test.status = TestStatus.ACTIVE
        
        # Add substantial data quickly
        large_data = {
            "control": {"impressions": 50000, "clicks": 2500, "conversions": 250},
            "test": {"impressions": 50000, "clicks": 3000, "conversions": 350}
        }
        
        # Add data efficiently
        for variation_id, data in large_data.items():
            variation = next(v for v in test.variations if v.variation_id == variation_id)
            variation.impressions = data["impressions"]
            variation.clicks = data["clicks"]
            variation.conversions = data["conversions"]
            variation.revenue = data["conversions"] * 100.0
            
            # Update calculated metrics
            ab_framework._update_variation_metrics(variation)
        
        # Time the statistical analysis
        analysis_start = time.time()
        await ab_framework._evaluate_test_results(test)
        analysis_time = time.time() - analysis_start
        
        print(f"Statistical analysis on 100k samples took {analysis_time:.3f}s")
        
        # Performance assertions
        assert analysis_time < 1.0  # Should analyze 100k samples in under 1 second
        assert test.current_result is not None
        assert test.current_result.winning_variation_id == "test"
        assert test.current_result.confidence_level > 0.9
    
    async def test_memory_usage_under_load(self, ab_framework):
        """Test memory usage patterns under sustained load."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_monitoring = True
        except ImportError:
            # Fallback when psutil is not available
            initial_memory = 0
            memory_monitoring = False
            print("psutil not available - skipping memory monitoring")
        
        # Create and process many tests
        num_cycles = 10
        tests_per_cycle = 10
        events_per_test = 1000
        
        for cycle in range(num_cycles):
            # Create tests
            tests = []
            for i in range(tests_per_cycle):
                config = {
                    "test_name": f"Memory Test {cycle}-{i}",
                    "test_type": "simple_ab",
                    "hypothesis": f"Memory test {cycle}-{i}",
                    "primary_metric": "conversion_rate"
                }
                
                variations = [
                    {
                        "variation_id": "control",
                        "name": "Control",
                        "description": "Control",
                        "traffic_percentage": 50.0,
                        "content_config": {}
                    },
                    {
                        "variation_id": "test",
                        "name": "Test",
                        "description": "Test",
                        "traffic_percentage": 50.0,
                        "content_config": {}
                    }
                ]
                
                test = await ab_framework.create_personalized_ab_test(
                    f"memory_user_{cycle}_{i}", config, variations
                )
                test.status = TestStatus.ACTIVE
                tests.append(test)
            
            # Add events to tests
            for test in tests:
                for event_num in range(events_per_test):
                    variation_id = "control" if event_num % 2 == 0 else "test"
                    event_type = ["impression", "click", "conversion"][event_num % 3]
                    
                    await ab_framework.record_test_event(
                        test.test_id, variation_id, event_type, value=10.0
                    )
            
            # Complete tests to trigger cleanup
            for test in tests:
                await ab_framework.conclude_test(test.test_id, f"memory_cycle_{cycle}")
            
            # Check memory usage if monitoring is available
            if memory_monitoring:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                print(f"Cycle {cycle}: Memory usage: {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
            else:
                print(f"Cycle {cycle}: Completed {tests_per_cycle} tests")
        
        if memory_monitoring:
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            total_memory_increase = final_memory - initial_memory
            print(f"Total memory increase: {total_memory_increase:.1f}MB")
            
            # Memory assertions (should not leak significantly)
            assert total_memory_increase < 100  # Should not increase by more than 100MB
        else:
            print("Memory monitoring skipped - psutil not available")
        
        # Framework state assertions (always check these)
        assert len(ab_framework.active_tests) == 0  # All tests should be cleaned up
        assert len(ab_framework.test_history) == num_cycles * tests_per_cycle
    
    async def test_response_time_consistency(self, ab_framework):
        """Test response time consistency under varying loads."""
        response_times = []
        
        # Create test
        test_config = {
            "test_name": "Response Time Test",
            "test_type": "simple_ab",
            "hypothesis": "Response time consistency test",
            "primary_metric": "conversion_rate"
        }
        
        variations = [
            {
                "variation_id": "control",
                "name": "Control",
                "description": "Control",
                "traffic_percentage": 50.0,
                "content_config": {}
            },
            {
                "variation_id": "test",
                "name": "Test",
                "description": "Test",
                "traffic_percentage": 50.0,
                "content_config": {}
            }
        ]
        
        test = await ab_framework.create_personalized_ab_test("response_user", test_config, variations)
        test.status = TestStatus.ACTIVE
        
        # Measure response times for different loads
        load_scenarios = [1, 10, 50, 100, 200, 500]
        
        for load in load_scenarios:
            scenario_times = []
            
            for i in range(load):
                start = time.time()
                
                await ab_framework.record_test_event(
                    test.test_id, "control", "impression"
                )
                
                end = time.time()
                scenario_times.append((end - start) * 1000)  # Convert to ms
            
            avg_response_time = statistics.mean(scenario_times)
            p95_response_time = statistics.quantiles(scenario_times, n=20)[18]  # 95th percentile
            
            response_times.append({
                "load": load,
                "avg_ms": avg_response_time,
                "p95_ms": p95_response_time
            })
            
            print(f"Load {load}: Avg={avg_response_time:.2f}ms, P95={p95_response_time:.2f}ms")
        
        # Performance assertions
        for rt in response_times:
            assert rt["avg_ms"] < 50  # Average response time should be <50ms
            assert rt["p95_ms"] < 100  # 95th percentile should be <100ms
        
        # Response time should not degrade significantly with load
        low_load_avg = response_times[0]["avg_ms"]
        high_load_avg = response_times[-1]["avg_ms"]
        degradation_factor = high_load_avg / low_load_avg
        
        assert degradation_factor < 5  # Response time should not degrade >5x


@pytest.mark.performance
class TestScalabilityLimits:
    """Test framework scalability limits."""
    
    def test_maximum_concurrent_tests(self):
        """Test framework behavior with maximum concurrent tests."""
        framework = ABTestingFramework()
        
        # Try to create a large number of tests
        max_tests = 1000
        created_tests = 0
        
        try:
            for i in range(max_tests):
                config = {
                    "test_name": f"Scale Test {i}",
                    "test_type": "simple_ab",
                    "hypothesis": f"Scale test {i}",
                    "primary_metric": "conversion_rate"
                }
                
                variations = [
                    {"variation_id": "control", "name": "Control", "description": "Control", 
                     "traffic_percentage": 50.0, "content_config": {}},
                    {"variation_id": "test", "name": "Test", "description": "Test", 
                     "traffic_percentage": 50.0, "content_config": {}}
                ]
                
                # Use asyncio.run for individual test creation in sync test
                test = asyncio.run(
                    framework.create_personalized_ab_test(f"scale_user_{i}", config, variations)
                )
                created_tests += 1
                
                # Stop if we hit performance degradation
                if i > 0 and i % 100 == 0:
                    print(f"Created {created_tests} tests successfully")
        
        except Exception as e:
            print(f"Hit limit at {created_tests} tests: {e}")
        
        print(f"Maximum concurrent tests: {created_tests}")
        assert created_tests >= 100  # Should handle at least 100 concurrent tests
    
    def test_maximum_variations_per_test(self):
        """Test maximum number of variations per test."""
        framework = ABTestingFramework()
        
        # Try creating test with many variations
        max_variations = 20
        
        config = {
            "test_name": "Max Variations Test",
            "test_type": "multivariate",
            "hypothesis": "Testing maximum variations",
            "primary_metric": "conversion_rate"
        }
        
        # Create variations with equal traffic split
        traffic_per_variation = 100.0 / max_variations
        variations = []
        
        for i in range(max_variations):
            variations.append({
                "variation_id": f"variation_{i}",
                "name": f"Variation {i}",
                "description": f"Test variation {i}",
                "traffic_percentage": traffic_per_variation,
                "content_config": {"variation_num": i}
            })
        
        try:
            test = asyncio.run(
                framework.create_personalized_ab_test("max_var_user", config, variations)
            )
            assert len(test.variations) == max_variations
            print(f"Successfully created test with {max_variations} variations")
        except Exception as e:
            print(f"Failed to create test with {max_variations} variations: {e}")
            assert False, f"Should support at least {max_variations} variations"