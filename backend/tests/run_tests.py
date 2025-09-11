#!/usr/bin/env python3
"""
Test runner script for Marketing AI Backend
Provides easy test execution with different configurations
"""

import argparse
import subprocess
import sys
import os


def run_command(cmd):
    """Run command and return result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0


def install_test_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    return run_command([
        sys.executable, "-m", "pip", "install", 
        "-r", "requirements.txt", "--quiet"
    ])


def run_tests(test_type=None, coverage=False, parallel=False, verbose=False):
    """Run tests with specified configuration."""
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test type filter
    if test_type:
        cmd.extend(["-m", test_type])
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=ml.ab_testing",
            "--cov=services", 
            "--cov=api.v1",
            "--cov-report=term-missing",
            "--cov-report=html:tests/htmlcov"
        ])
    
    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Add verbose output
    if verbose:
        cmd.extend(["-v", "-s"])
    
    # Add test directory
    cmd.append("tests/")
    
    return run_command(cmd)


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Marketing AI Backend Test Runner")
    
    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "performance", "api", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true", 
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--install-deps", "-i",
        action="store_true",
        help="Install test dependencies first"
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run quick tests only (unit + integration)"
    )
    
    parser.add_argument(
        "--benchmark", "-b",
        action="store_true",
        help="Run performance benchmarks"
    )
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    print("🧪 Marketing AI Backend Test Runner")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            print("❌ Failed to install test dependencies")
            sys.exit(1)
        print("✅ Test dependencies installed")
    
    # Determine test type
    test_type = None
    if args.quick:
        test_type = "unit or integration"
    elif args.benchmark:
        test_type = "performance"
    elif args.type != "all":
        test_type = args.type
    
    print(f"Running tests: {test_type or 'all'}")
    
    # Run tests
    success = run_tests(
        test_type=test_type,
        coverage=args.coverage,
        parallel=args.parallel,
        verbose=args.verbose
    )
    
    if success:
        print("\n✅ All tests passed!")
        
        if args.coverage:
            print("📊 Coverage report generated in tests/htmlcov/")
        
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()