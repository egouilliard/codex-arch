"""
Configuration and utilities for end-to-end tests.

This module provides configuration settings and utility functions for running
end-to-end tests that verify the entire system's functionality.
"""

import os
import json
import logging
from pathlib import Path

# Configure logging for E2E tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("e2e_tests")

# Default settings for E2E tests
E2E_CONFIG = {
    # Test timeout settings (in seconds)
    "DEFAULT_TIMEOUT": 30,  # Default timeout for most operations
    "API_POLL_INTERVAL": 0.5,  # Interval to poll API for status
    "API_MAX_RETRIES": 20,  # Maximum number of retries for API polling
    
    # Test data paths
    "SAMPLE_REPOS": {
        "small": "tests/fixtures/small_repo",
        "medium": "tests/fixtures/medium_repo",
        "large": "tests/fixtures/large_repo"
    },
    
    # API test configuration
    "API_TEST_USER": "test_user",
    "API_TEST_PASSWORD": "test_password",
    
    # CLI test configuration
    "CLI_DEFAULT_OPTIONS": {
        "include_python": True,
        "include_javascript": False,
        "generate_graph": True,
        "generate_summary": True,
        "verbose": True
    }
}


def load_fixture(fixture_path):
    """
    Load a fixture file for testing.
    
    Args:
        fixture_path: Path to the fixture file relative to the fixtures directory
        
    Returns:
        The content of the fixture file
    """
    base_path = Path(__file__).parent / "fixtures"
    full_path = base_path / fixture_path
    
    with open(full_path, 'r') as f:
        content = f.read()
        
    # For JSON fixtures, parse into Python objects
    if fixture_path.endswith(".json"):
        return json.loads(content)
    
    return content


def wait_for_completion(check_function, max_retries=None, poll_interval=None):
    """
    Wait for an operation to complete by periodically checking its status.
    
    Args:
        check_function: Function that returns True when operation is complete
        max_retries: Maximum number of retries (defaults to E2E_CONFIG["API_MAX_RETRIES"])
        poll_interval: Time between checks in seconds (defaults to E2E_CONFIG["API_POLL_INTERVAL"])
        
    Returns:
        True if operation completed, False if timed out
    """
    if max_retries is None:
        max_retries = E2E_CONFIG["API_MAX_RETRIES"]
        
    if poll_interval is None:
        poll_interval = E2E_CONFIG["API_POLL_INTERVAL"]
    
    import time
    
    for _ in range(max_retries):
        if check_function():
            return True
        time.sleep(poll_interval)
    
    return False


def verify_json_structure(json_data, required_fields, path=""):
    """
    Verify that JSON data contains all required fields.
    
    Args:
        json_data: The JSON data to verify as a Python dictionary
        required_fields: Dictionary mapping field names to their expected types
                        or nested field requirements
        path: Current path in the JSON structure (for error reporting)
        
    Returns:
        (bool, str): Tuple of (is_valid, error_message)
    """
    for field, requirement in required_fields.items():
        field_path = f"{path}.{field}" if path else field
        
        # Check if field exists
        if field not in json_data:
            return False, f"Missing required field: {field_path}"
        
        # If requirement is a type, check type
        if isinstance(requirement, type):
            if not isinstance(json_data[field], requirement):
                return False, f"Field {field_path} has wrong type: expected {requirement.__name__}, got {type(json_data[field]).__name__}"
        
        # If requirement is a dict, recursively check structure
        elif isinstance(requirement, dict):
            if not isinstance(json_data[field], dict):
                return False, f"Field {field_path} should be an object/dictionary"
            
            # Recursive check
            is_valid, error = verify_json_structure(json_data[field], requirement, field_path)
            if not is_valid:
                return False, error
        
        # If requirement is a list with a single element, check each item in the array
        elif isinstance(requirement, list) and len(requirement) == 1:
            if not isinstance(json_data[field], list):
                return False, f"Field {field_path} should be an array"
            
            # Check each item in the array
            for i, item in enumerate(json_data[field]):
                item_path = f"{field_path}[{i}]"
                
                if isinstance(requirement[0], type):
                    if not isinstance(item, requirement[0]):
                        return False, f"Item {item_path} has wrong type: expected {requirement[0].__name__}, got {type(item).__name__}"
                
                elif isinstance(requirement[0], dict):
                    if not isinstance(item, dict):
                        return False, f"Item {item_path} should be an object/dictionary"
                    
                    # Recursive check
                    is_valid, error = verify_json_structure(item, requirement[0], item_path)
                    if not is_valid:
                        return False, error
    
    return True, "Valid" 