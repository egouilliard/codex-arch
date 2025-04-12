#!/bin/bash

# This script runs the test suite with coverage reporting

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Activate virtual environment if present
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install test dependencies
echo "Checking test dependencies..."
pip install -r requirements.txt

# Create directories for coverage reports
mkdir -p coverage_reports

# Run the tests with different markers
echo -e "\n=== Running Unit Tests ===\n"
python -m pytest tests/ -v -m "unit or not marked" --cov=codex_arch --cov-report=term --cov-report=xml:coverage_reports/coverage.xml

echo -e "\n=== Running All Tests ===\n"
python -m pytest tests/ -v --cov=codex_arch --cov-report=html:coverage_reports/html

# Print coverage summary
echo -e "\n=== Coverage Summary ===\n"
python -m coverage report

# Optional: Open coverage report in browser
if [ "$1" == "--open" ]; then
    echo "Opening coverage report in browser..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open coverage_reports/html/index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open coverage_reports/html/index.html
    elif [[ "$OSTYPE" == "msys" ]]; then
        start coverage_reports/html/index.html
    fi
fi

echo -e "\nDone. Coverage reports are available in the coverage_reports directory." 