# Marketing AI Backend Test Suite Makefile
# Convenient commands for running tests

.PHONY: help install test test-unit test-integration test-performance test-api test-coverage test-quick test-all clean

# Default target
help:
	@echo "Marketing AI Backend Test Suite"
	@echo "==============================="
	@echo ""
	@echo "Available commands:"
	@echo "  install          Install test dependencies"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests only"
	@echo "  test-api         Run API tests only"
	@echo "  test-coverage    Run tests with coverage report"
	@echo "  test-quick       Run quick tests (unit + integration)"
	@echo "  test-parallel    Run tests in parallel"
	@echo "  test-verbose     Run tests with verbose output"
	@echo "  benchmark        Run performance benchmarks"
	@echo "  clean            Clean test artifacts"

# Install test dependencies  
install:
	pip install -r requirements.txt

# Run all tests
test:
	python -m pytest tests/

# Run specific test categories
test-unit:
	python -m pytest tests/ -m unit

test-integration:
	python -m pytest tests/ -m integration

test-performance:
	python -m pytest tests/ -m performance

test-api:
	python -m pytest tests/ -m api

# Run tests with coverage
test-coverage:
	python -m pytest tests/ \
		--cov=ml.ab_testing \
		--cov=services \
		--cov=api.v1 \
		--cov-report=term-missing \
		--cov-report=html:tests/htmlcov

# Quick tests (unit + integration)
test-quick:
	python -m pytest tests/ -m "unit or integration"

# Parallel test execution
test-parallel:
	python -m pytest tests/ -n auto

# Verbose test output
test-verbose:
	python -m pytest tests/ -v -s

# Performance benchmarks
benchmark:
	python -m pytest tests/ -m performance --durations=0

# Run tests with timing information
test-timing:
	python -m pytest tests/ --durations=10

# Run only failed tests
test-failed:
	python -m pytest tests/ --lf

# Run failed tests first
test-failed-first:
	python -m pytest tests/ --ff

# Generate HTML test report
test-report:
	python -m pytest tests/ --html=tests/report.html --self-contained-html

# Run specific test file
test-file:
	python -m pytest tests/$(FILE) -v

# Run specific test function
test-function:
	python -m pytest tests/ -k "$(FUNCTION)" -v

# Debug specific test
test-debug:
	python -m pytest tests/$(FILE)::$(CLASS)::$(METHOD) -v -s --pdb

# Clean test artifacts
clean:
	rm -rf tests/htmlcov/
	rm -rf tests/.pytest_cache/
	rm -rf tests/report.html
	find tests/ -name "*.pyc" -delete
	find tests/ -name "__pycache__" -type d -exec rm -rf {} +

# Lint tests
lint-tests:
	flake8 tests/ --max-line-length=120
	pylint tests/ --disable=missing-docstring

# Format test code
format-tests:
	black tests/
	isort tests/

# Check test code quality
quality-check:
	black --check tests/
	isort --check tests/
	flake8 tests/

# Run full test suite (CI-like)
test-ci:
	python -m pytest tests/ \
		--cov=ml.ab_testing \
		--cov=services \
		--cov=api.v1 \
		--cov-report=xml:tests/coverage.xml \
		--cov-report=term \
		--junit-xml=tests/junit.xml \
		--durations=10

# Examples of running specific tests
examples:
	@echo "Example commands:"
	@echo "  make test-file FILE=unit/ab_testing/test_framework_core.py"
	@echo "  make test-function FUNCTION=test_create_simple_ab_test"
	@echo "  make test-debug FILE=unit/ab_testing/test_framework_core.py CLASS=TestABTestingFrameworkCore METHOD=test_create_simple_ab_test"