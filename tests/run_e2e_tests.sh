#!/bin/bash
#
# End-to-End Test Runner for Codex-Arch
#
# This script runs the end-to-end tests for the Codex-Arch system,
# configuring the environment appropriately and generating reports.
#

# Setup colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}===========================================================${NC}"
echo -e "${BLUE}            Codex-Arch End-to-End Test Runner              ${NC}"
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

# Ensure dependencies are installed
echo -e "${BLUE}Ensuring dependencies are installed...${NC}"
pip install -q -e ".[test]" || { echo -e "${RED}Failed to install dependencies${NC}"; exit 1; }

# Create test output directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_OUTPUT_DIR="tests/output/${TIMESTAMP}"
mkdir -p "${TEST_OUTPUT_DIR}"
echo -e "${BLUE}Test output will be saved to: ${TEST_OUTPUT_DIR}${NC}"

# Parse command line arguments
VERBOSE=""
SPECIFIC_TESTS=""
SKIP_SLOW=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -m|--mark)
            SPECIFIC_TESTS="-m $2"
            shift 2
            ;;
        --skip-slow)
            SKIP_SLOW="-k 'not slow'"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [-v|--verbose] [-m|--mark MARKER] [--skip-slow]"
            exit 1
            ;;
    esac
done

# If no specific tests are specified, run all e2e tests
if [[ -z "${SPECIFIC_TESTS}" ]]; then
    SPECIFIC_TESTS="-m e2e"
fi

# Set environment variables for testing
export TESTING=true
export LOG_LEVEL=INFO

# Run the tests
echo -e "${BLUE}Running end-to-end tests...${NC}"
echo -e "${BLUE}Command: pytest ${VERBOSE} ${SPECIFIC_TESTS} ${SKIP_SLOW} --junitxml=${TEST_OUTPUT_DIR}/junit.xml tests/${NC}"

pytest ${VERBOSE} ${SPECIFIC_TESTS} ${SKIP_SLOW} \
    --junitxml="${TEST_OUTPUT_DIR}/junit.xml" \
    --html="${TEST_OUTPUT_DIR}/report.html" \
    --self-contained-html \
    tests/

# Check the result
EXIT_CODE=$?
if [[ ${EXIT_CODE} -eq 0 ]]; then
    echo -e "${GREEN}All end-to-end tests passed!${NC}"
else
    echo -e "${RED}Some end-to-end tests failed. Check the report for details.${NC}"
    echo -e "${BLUE}Test report: ${TEST_OUTPUT_DIR}/report.html${NC}"
fi

echo -e "${BLUE}===========================================================${NC}"
exit ${EXIT_CODE} 