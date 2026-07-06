#!/bin/bash
# FirAI Backend Test Runner

set -e

echo "🧪 FirAI Backend Test Suite"
echo "=============================="

cd "$(dirname "$0")"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Determine test scope from argument
SCOPE=${1:-all}

case $SCOPE in
    all)
        echo "Running all tests with coverage..."
        pytest --cov=. --cov-report=html --cov-report=term-missing -v
        echo "✅ Coverage report generated in htmlcov/index.html"
        ;;
    api)
        echo "Running API tests..."
        pytest tests/test_api_endpoints.py -v
        ;;
    ai)
        echo "Running AI model tests..."
        pytest tests/test_ai_models.py -v
        ;;
    services)
        echo "Running service tests..."
        pytest tests/test_services.py -v
        ;;
    fast)
        echo "Running tests without coverage..."
        pytest -v
        ;;
    coverage)
        echo "Running tests with coverage report..."
        pytest --cov=. --cov-report=html --cov-report=term-missing
        echo "✅ Coverage report: htmlcov/index.html"
        ;;
    *)
        echo "Usage: ./run_tests.sh [all|api|ai|services|fast|coverage]"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed successfully!"
