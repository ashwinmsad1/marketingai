# Marketing AI Backend Test Suite

This directory contains comprehensive tests for the Marketing AI backend, with a focus on A/B testing framework functionality.

## Test Structure

```
tests/
├── unit/                    # Unit tests - fast, isolated
│   ├── ab_testing/         # A/B testing framework unit tests
│   │   ├── test_framework_core.py      # Core functionality tests
│   │   ├── test_statistical_analysis.py # Statistical methods tests
│   │   └── test_ai_recommendations.py   # AI recommendations tests
│   ├── services/           # Service layer unit tests
│   └── engines/           # Engine component unit tests
├── integration/            # Integration tests - component interactions
│   └── ab_testing/        # A/B testing integration tests
│       ├── test_end_to_end.py          # Complete workflow tests
│       ├── test_ab_integration.py      # Framework integration tests
│       └── debug_ab_comprehensive.py   # Comprehensive debug tests
├── performance/           # Performance and load tests
│   └── ab_testing/       # A/B testing performance tests
│       ├── test_load_performance.py    # Load and scalability tests
│       └── production_readiness_test.py # Production readiness validation
├── api/                  # API endpoint tests
│   └── v1/              # API v1 tests
│       └── test_personalization_ab_testing.py # A/B testing API tests
├── fixtures/            # Test data fixtures
│   └── ab_testing_fixtures.py          # A/B testing test fixtures
├── utils/              # Test utilities and helpers
│   └── test_helpers.py                 # Common test utilities
├── conftest.py         # Pytest configuration and shared fixtures
├── pytest.ini         # Pytest settings
└── README.md          # This file
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests that test individual components:
- **Framework Core**: Test creation, event recording, metrics calculation
- **Statistical Analysis**: Statistical tests, confidence intervals, power analysis
- **AI Recommendations**: Claude integration, fallback recommendations

### Integration Tests (`tests/integration/`)
Tests that verify component interactions:
- **End-to-End**: Complete A/B test lifecycle from creation to conclusion
- **Service Integration**: Framework integration with personalization service
- **Cross-Component**: Multiple system interactions

### Performance Tests (`tests/performance/`)
Tests that measure performance and scalability:
- **Load Testing**: High-volume event processing, concurrent test management
- **Memory Usage**: Memory leak detection, resource cleanup
- **Response Times**: Latency measurements under varying loads

### API Tests (`tests/api/`)
Tests for HTTP API endpoints:
- **CRUD Operations**: Create, read, update, delete A/B tests
- **Request Validation**: Input validation, error handling
- **Response Format**: Correct data transformation

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-asyncio pytest-cov pytest-timeout
```

### Run All Tests
```bash
pytest
```

### Run by Category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Performance tests only
pytest -m performance

# API tests only
pytest -m api
```

### Run Specific Test Files
```bash
# A/B testing core functionality
pytest tests/unit/ab_testing/test_framework_core.py

# End-to-end integration
pytest tests/integration/ab_testing/test_end_to_end.py

# Performance testing
pytest tests/performance/ab_testing/test_load_performance.py
```

### Run with Coverage
```bash
pytest --cov=ml.ab_testing --cov-report=html
```

### Run Performance Tests with Timing
```bash
pytest -m performance --durations=0 -v
```

## Test Configuration

### Markers
- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.api`: API endpoint tests
- `@pytest.mark.slow`: Tests that take longer to run
- `@pytest.mark.asyncio`: Asynchronous tests

### Fixtures
Common fixtures are defined in `conftest.py`:
- `ab_framework`: Fresh A/B testing framework instance
- `personalization_service`: Personalization service with A/B testing
- `sample_test_config`: Sample test configuration
- `sample_variations`: Sample test variations
- `active_test`: Active test with variations
- `mock_user`: Mock user for API tests

### Custom Fixtures
Additional fixtures in `fixtures/ab_testing_fixtures.py`:
- `sample_test_variation`: Individual test variation
- `test_with_data`: Test with performance data
- `multivariate_test`: Test with multiple variations
- `performance_scenarios`: Various performance test scenarios

## Test Utilities

### EventSimulator (`tests/utils/test_helpers.py`)
Utility for simulating realistic A/B test traffic:
```python
await EventSimulator.simulate_realistic_traffic(
    framework, test_id, {
        "control": {"impressions": 1000, "clicks": 50, "conversions": 5},
        "test": {"impressions": 1000, "clicks": 75, "conversions": 10}
    }
)
```

### PerformanceProfiler
Utility for profiling test operations:
```python
profiler = PerformanceProfiler()
result = await profiler.profile_operation(
    framework.create_personalized_ab_test,
    "test_creation",
    user_id, config, variations
)
print(profiler.get_stats())
```

### TestDataValidator
Utility for validating test data integrity:
```python
issues = TestDataValidator.validate_test_structure(test)
assert len(issues) == 0, f"Test validation failed: {issues}"
```

## Writing New Tests

### Unit Test Example
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_feature(ab_framework, sample_test_config):
    """Test my new feature."""
    # Arrange
    test = await ab_framework.create_personalized_ab_test(
        "user_123", sample_test_config, sample_variations
    )
    
    # Act
    result = await ab_framework.my_new_feature(test.test_id)
    
    # Assert
    assert result is not None
    assert result.success is True
```

### Performance Test Example
```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_feature_performance(ab_framework):
    """Test feature performance under load."""
    start_time = time.time()
    
    # Perform operations
    for i in range(1000):
        await ab_framework.fast_operation()
    
    duration = time.time() - start_time
    operations_per_second = 1000 / duration
    
    assert operations_per_second > 500  # Should be >500 ops/sec
```

### API Test Example
```python
@pytest.mark.api
async def test_api_endpoint(client, mock_user):
    """Test API endpoint."""
    response = client.post(
        "/api/v1/personalization/ab-tests",
        json={"campaign_name": "Test", ...}
    )
    
    assert response.status_code == 200
    assert response.json()["test_id"] is not None
```

## Continuous Integration

Tests are designed to run in CI environments:
- All tests should complete in under 5 minutes
- Performance tests have reasonable thresholds for CI machines
- Tests are isolated and can run in parallel
- Comprehensive coverage reporting

## Debugging Tests

### Verbose Output
```bash
pytest -v -s  # Verbose with stdout
```

### Debug Specific Test
```bash
pytest tests/unit/ab_testing/test_framework_core.py::TestABTestingFrameworkCore::test_create_simple_ab_test -v -s
```

### Run Failed Tests Only
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Isolation**: Tests should be independent and not rely on external state
4. **Performance**: Performance tests should have realistic expectations
5. **Async**: Use `@pytest.mark.asyncio` for async tests
6. **Mocking**: Mock external dependencies appropriately
7. **Coverage**: Aim for high test coverage while focusing on critical paths

## Contributing

When adding new features to the A/B testing framework:

1. Add unit tests for individual components
2. Add integration tests for feature interactions
3. Add performance tests if the feature affects performance
4. Add API tests if the feature exposes new endpoints
5. Update fixtures if new test data is needed
6. Update this README if new test categories are added