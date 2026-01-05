#!/bin/bash
# Test runner script for Open-Instruct

set -e

echo "==================================="
echo "Running Open-Instruct Test Suite"
echo "==================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run tests with coverage (excluding spikes directory)
echo "Running tests with coverage..."
pytest tests/unit tests/mocked tests/integration \
    -v \
    --tb=short \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=json \
    --cov-fail-under=85 \
    --ignore=tests/spikes

echo ""
echo "==================================="
echo "Test Results Summary"
echo "==================================="
echo ""
echo "Coverage reports generated:"
echo "  - Terminal output (above)"
echo "  - HTML: htmlcov/index.html"
echo "  - JSON: coverage.json"
echo ""
echo "To view HTML coverage report:"
echo "  open htmlcov/index.html"
echo ""
