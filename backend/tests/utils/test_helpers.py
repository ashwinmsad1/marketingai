"""
Test utility functions and helpers
"""

import asyncio
import time
from typing import List, Dict, Any, Callable
from contextlib import asynccontextmanager

from ml.ab_testing.ab_testing_framework import ABTestingFramework, PersonalizedTest


class TestTimer:
    """Utility for measuring test execution time."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timing."""
        self.start_time = time.time()
    
    def stop(self):
        """Stop timing."""
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed * 1000


@asynccontextmanager
async def async_timer():
    """Async context manager for timing operations."""
    timer = TestTimer()
    timer.start()
    try:
        yield timer
    finally:
        timer.stop()


class EventSimulator:
    """Utility for simulating realistic A/B test events."""
    
    @staticmethod
    async def simulate_realistic_traffic(
        framework: ABTestingFramework,
        test_id: str,
        traffic_patterns: Dict[str, Dict[str, int]],
        delay_between_events: float = 0.0
    ):
        """
        Simulate realistic traffic patterns for A/B tests.
        
        Args:
            framework: AB testing framework instance
            test_id: Test ID to record events for
            traffic_patterns: Dict mapping variation_id to event counts
            delay_between_events: Delay between events in seconds
        """
        for variation_id, events in traffic_patterns.items():
            # Record impressions first
            for _ in range(events.get("impressions", 0)):
                await framework.record_test_event(test_id, variation_id, "impression")
                if delay_between_events > 0:
                    await asyncio.sleep(delay_between_events)
            
            # Record clicks
            for _ in range(events.get("clicks", 0)):
                await framework.record_test_event(test_id, variation_id, "click")
                if delay_between_events > 0:
                    await asyncio.sleep(delay_between_events)
            
            # Record conversions with value
            for _ in range(events.get("conversions", 0)):
                value = events.get("conversion_value", 100.0)
                await framework.record_test_event(test_id, variation_id, "conversion", value=value)
                if delay_between_events > 0:
                    await asyncio.sleep(delay_between_events)
    
    @staticmethod
    async def simulate_gradual_traffic_buildup(
        framework: ABTestingFramework,
        test_id: str,
        variation_id: str,
        total_impressions: int,
        buildup_days: int = 7
    ):
        """Simulate gradual traffic buildup over time."""
        daily_impressions = total_impressions // buildup_days
        
        for day in range(buildup_days):
            # Simulate daily traffic with some randomness
            day_impressions = daily_impressions + (day * 10)  # Gradual increase
            
            for _ in range(day_impressions):
                await framework.record_test_event(test_id, variation_id, "impression")
    
    @staticmethod
    def generate_conversion_funnel(
        impressions: int,
        ctr: float = 0.05,
        conversion_rate: float = 0.10
    ) -> Dict[str, int]:
        """Generate realistic conversion funnel numbers."""
        clicks = int(impressions * ctr)
        conversions = int(clicks * conversion_rate)
        
        return {
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions
        }


class PerformanceProfiler:
    """Utility for profiling test performance."""
    
    def __init__(self):
        self.measurements = []
    
    async def profile_operation(
        self,
        operation: Callable,
        operation_name: str,
        *args,
        **kwargs
    ) -> Any:
        """Profile an async operation."""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)
            
            success = True
            error = None
            
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.measurements.append({
            "operation": operation_name,
            "duration": duration,
            "success": success,
            "error": error,
            "timestamp": start_time
        })
        
        if not success:
            raise Exception(error)
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.measurements:
            return {}
        
        durations = [m["duration"] for m in self.measurements if m["success"]]
        
        if not durations:
            return {"error": "No successful operations"}
        
        return {
            "total_operations": len(self.measurements),
            "successful_operations": len(durations),
            "failure_rate": (len(self.measurements) - len(durations)) / len(self.measurements),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations)
        }
    
    def print_report(self):
        """Print performance report."""
        stats = self.get_stats()
        
        if "error" in stats:
            print(f"Performance Report: {stats['error']}")
            return
        
        print("Performance Report:")
        print(f"  Total Operations: {stats['total_operations']}")
        print(f"  Success Rate: {(1 - stats['failure_rate']) * 100:.1f}%")
        print(f"  Average Duration: {stats['avg_duration'] * 1000:.2f}ms")
        print(f"  Min Duration: {stats['min_duration'] * 1000:.2f}ms")
        print(f"  Max Duration: {stats['max_duration'] * 1000:.2f}ms")
        print(f"  Total Time: {stats['total_duration']:.2f}s")


class TestDataValidator:
    """Utility for validating test data integrity."""
    
    @staticmethod
    def validate_test_structure(test: PersonalizedTest) -> List[str]:
        """Validate test structure and return list of issues."""
        issues = []
        
        # Basic validation
        if not test.test_id:
            issues.append("Test ID is missing")
        
        if not test.user_id:
            issues.append("User ID is missing")
        
        if not test.test_name:
            issues.append("Test name is missing")
        
        if not test.variations:
            issues.append("No variations defined")
        elif len(test.variations) < 2:
            issues.append("Test must have at least 2 variations")
        
        # Traffic allocation validation
        if test.traffic_allocation:
            total_traffic = sum(test.traffic_allocation.values())
            if abs(total_traffic - 100.0) > 0.01:
                issues.append(f"Traffic allocation sums to {total_traffic}%, should be 100%")
        
        # Variation validation
        for i, variation in enumerate(test.variations):
            if not variation.variation_id:
                issues.append(f"Variation {i} missing ID")
            
            if not variation.name:
                issues.append(f"Variation {i} missing name")
            
            if variation.traffic_percentage < 0 or variation.traffic_percentage > 100:
                issues.append(f"Variation {i} has invalid traffic percentage: {variation.traffic_percentage}")
        
        # Date validation
        if test.start_date and test.planned_end_date:
            if test.start_date >= test.planned_end_date:
                issues.append("Start date must be before end date")
        
        return issues
    
    @staticmethod
    def validate_variation_data_consistency(test: PersonalizedTest) -> List[str]:
        """Validate variation data consistency."""
        issues = []
        
        for variation in test.variations:
            # Check that clicks <= impressions
            if variation.clicks > variation.impressions:
                issues.append(f"Variation {variation.variation_id}: clicks ({variation.clicks}) > impressions ({variation.impressions})")
            
            # Check that conversions <= clicks
            if variation.conversions > variation.clicks:
                issues.append(f"Variation {variation.variation_id}: conversions ({variation.conversions}) > clicks ({variation.clicks})")
            
            # Check calculated metrics
            if variation.impressions > 0:
                expected_ctr = (variation.clicks / variation.impressions) * 100
                if abs(variation.ctr - expected_ctr) > 0.1:
                    issues.append(f"Variation {variation.variation_id}: CTR calculation mismatch")
            
            if variation.clicks > 0:
                expected_cr = (variation.conversions / variation.clicks) * 100
                if abs(variation.conversion_rate - expected_cr) > 0.1:
                    issues.append(f"Variation {variation.variation_id}: Conversion rate calculation mismatch")
        
        return issues


class ConcurrencyTestHelper:
    """Helper for testing concurrent operations."""
    
    @staticmethod
    async def run_concurrent_operations(
        operations: List[Callable],
        max_concurrency: int = 10
    ) -> List[Any]:
        """Run operations with limited concurrency."""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def limited_operation(op):
            async with semaphore:
                if asyncio.iscoroutinefunction(op):
                    return await op()
                else:
                    return op()
        
        tasks = [limited_operation(op) for op in operations]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    @staticmethod
    async def simulate_concurrent_users(
        user_operations: Dict[str, List[Callable]],
        delay_between_operations: float = 0.1
    ) -> Dict[str, List[Any]]:
        """Simulate multiple users performing operations concurrently."""
        results = {}
        
        async def simulate_user(user_id: str, operations: List[Callable]):
            user_results = []
            for operation in operations:
                try:
                    if asyncio.iscoroutinefunction(operation):
                        result = await operation()
                    else:
                        result = operation()
                    user_results.append(result)
                except Exception as e:
                    user_results.append(f"Error: {e}")
                
                await asyncio.sleep(delay_between_operations)
            
            return user_results
        
        tasks = [
            simulate_user(user_id, operations)
            for user_id, operations in user_operations.items()
        ]
        
        user_results = await asyncio.gather(*tasks)
        
        for i, user_id in enumerate(user_operations.keys()):
            results[user_id] = user_results[i]
        
        return results


def assert_performance_within_limits(
    duration: float,
    expected_max: float,
    operation_name: str = "Operation"
):
    """Assert that operation completed within performance limits."""
    assert duration <= expected_max, (
        f"{operation_name} took {duration:.3f}s, expected <{expected_max}s"
    )


def assert_throughput_meets_requirement(
    operations_count: int,
    duration: float,
    min_throughput: float,
    operation_name: str = "Operations"
):
    """Assert that throughput meets minimum requirements."""
    actual_throughput = operations_count / duration
    assert actual_throughput >= min_throughput, (
        f"{operation_name} throughput was {actual_throughput:.0f}/s, expected >={min_throughput}/s"
    )