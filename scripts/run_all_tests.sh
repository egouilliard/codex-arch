#!/bin/bash
#
# Run All Tests Script for Codex-Arch
#
# This script runs all types of tests (unit, integration, and end-to-end)
# with proper reporting and coverage analysis.
#

# Setup colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}===========================================================${NC}"
echo -e "${BLUE}               Codex-Arch Test Runner                      ${NC}"
echo -e "${BLUE}===========================================================${NC}"

# Ensure we're in the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}/.." || { echo "Failed to change to project root directory"; exit 1; }

# Check if virtual environment is active
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}Virtual environment not activated. Attempting to activate...${NC}"
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    else
        echo -e "${RED}Virtual environment not found. Please create and activate it first.${NC}"
        echo "Run: python -m venv venv && source venv/bin/activate && pip install -e ."
        exit 1
    fi
fi

# Parse command line arguments
VERBOSE=0
SKIP_E2E=0
COVERAGE_ONLY=0
CI_MODE=0
JUNIT_REPORT=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        --skip-e2e)
            SKIP_E2E=1
            shift
            ;;
        --coverage-only)
            COVERAGE_ONLY=1
            shift
            ;;
        --ci)
            CI_MODE=1
            JUNIT_REPORT=1
            shift
            ;;
        --junit)
            JUNIT_REPORT=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -v, --verbose       Enable verbose output"
            echo "  --skip-e2e          Skip end-to-end tests"
            echo "  --coverage-only     Only run coverage report on existing data"
            echo "  --ci                Run in CI mode (includes JUnit reports)"
            echo "  --junit             Generate JUnit reports"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Run '$0 --help' for usage information."
            exit 1
            ;;
    esac
done

# Create test output directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_OUTPUT_DIR="tests/output/${TIMESTAMP}"
mkdir -p "${TEST_OUTPUT_DIR}"
echo -e "${BLUE}Test output will be saved to: ${TEST_OUTPUT_DIR}${NC}"

# Ensure dependencies are installed
if [[ $COVERAGE_ONLY -eq 0 ]]; then
    echo -e "${BLUE}Ensuring dependencies are installed...${NC}"
    pip install -q -e ".[test]" || { echo -e "${RED}Failed to install dependencies${NC}"; exit 1; }
    pip install -q pytest-cov coverage pytest-html || { echo -e "${RED}Failed to install test dependencies${NC}"; exit 1; }
fi

# Setup pytest options
PYTEST_OPTS=""
if [[ $VERBOSE -eq 1 ]]; then
    PYTEST_OPTS="${PYTEST_OPTS} -v"
fi

if [[ $JUNIT_REPORT -eq 1 ]]; then
    PYTEST_OPTS="${PYTEST_OPTS} --junitxml=${TEST_OUTPUT_DIR}/junit.xml"
fi

# Run the tests or gather coverage
if [[ $COVERAGE_ONLY -eq 0 ]]; then
    # Run unit tests
    echo -e "${BLUE}Running unit tests...${NC}"
    python -m pytest ${PYTEST_OPTS} tests/ -k "not integration and not e2e" \
        --cov=codex_arch \
        --cov-report=term \
        --cov-report=xml:${TEST_OUTPUT_DIR}/coverage.xml \
        --html=${TEST_OUTPUT_DIR}/unit_report.html \
        --self-contained-html
    UNIT_RESULT=$?

    # Run integration tests
    echo -e "${BLUE}Running integration tests...${NC}"
    python -m pytest ${PYTEST_OPTS} tests/ -m "integration" \
        --cov=codex_arch \
        --cov-append \
        --cov-report=term \
        --cov-report=xml:${TEST_OUTPUT_DIR}/coverage.xml \
        --html=${TEST_OUTPUT_DIR}/integration_report.html \
        --self-contained-html
    INTEGRATION_RESULT=$?

    # Run end-to-end tests if not skipped
    if [[ $SKIP_E2E -eq 0 ]]; then
        echo -e "${BLUE}Running end-to-end tests...${NC}"
        chmod +x tests/run_e2e_tests.sh
        
        # Run the E2E tests with the appropriate options
        E2E_ARGS=""
        if [[ $VERBOSE -eq 1 ]]; then
            E2E_ARGS="${E2E_ARGS} -v"
        fi
        
        if [[ $JUNIT_REPORT -eq 1 ]]; then
            E2E_ARGS="${E2E_ARGS} --junit"
        fi
        
        ./tests/run_e2e_tests.sh ${E2E_ARGS}
        E2E_RESULT=$?
    else
        echo -e "${YELLOW}Skipping end-to-end tests${NC}"
        E2E_RESULT=0
    fi
else
    echo -e "${BLUE}Skipping tests, running coverage report only...${NC}"
    UNIT_RESULT=0
    INTEGRATION_RESULT=0
    E2E_RESULT=0
fi

# Generate coverage report
echo -e "${BLUE}Generating coverage report...${NC}"
coverage report --omit="tests/*,*/site-packages/*" --fail-under=80 || true
coverage html -d ${TEST_OUTPUT_DIR}/coverage
coverage xml -o ${TEST_OUTPUT_DIR}/coverage.xml

# Determine overall test status
if [ $UNIT_RESULT -eq 0 ] && [ $INTEGRATION_RESULT -eq 0 ] && [ $E2E_RESULT -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}Some tests failed!${NC}"
    echo -e "Unit tests: $([ $UNIT_RESULT -eq 0 ] && echo "${GREEN}Passed${NC}" || echo "${RED}Failed${NC}")"
    echo -e "Integration tests: $([ $INTEGRATION_RESULT -eq 0 ] && echo "${GREEN}Passed${NC}" || echo "${RED}Failed${NC}")"
    if [[ $SKIP_E2E -eq 0 ]]; then
        echo -e "End-to-end tests: $([ $E2E_RESULT -eq 0 ] && echo "${GREEN}Passed${NC}" || echo "${RED}Failed${NC}")"
    fi
    EXIT_CODE=1
fi

# Print report path
echo -e "${BLUE}Test reports are available at:${NC}"
echo -e "  Unit tests:        ${TEST_OUTPUT_DIR}/unit_report.html"
echo -e "  Integration tests: ${TEST_OUTPUT_DIR}/integration_report.html"
if [[ $SKIP_E2E -eq 0 ]]; then
    echo -e "  E2E tests:         ${TEST_OUTPUT_DIR}/report.html"
fi
echo -e "  Coverage:          ${TEST_OUTPUT_DIR}/coverage/index.html"

echo -e "${BLUE}===========================================================${NC}"
exit ${EXIT_CODE} 