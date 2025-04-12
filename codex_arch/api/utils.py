"""
Utility functions for the Codex-Arch REST API.
"""

import os
import uuid
import json
import logging
import functools
import time
from typing import Dict, Any, Optional, Callable, List, Set, Union
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import request, jsonify, current_app, g

logger = logging.getLogger(__name__)

def generate_unique_id() -> str:
    """Generate a unique ID for a job/session."""
    return str(uuid.uuid4())

def get_allowed_file_extensions() -> Set[str]:
    """Get allowed file extensions for uploads."""
    return {'zip', 'tar', 'gz', 'py', 'js', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'php', 'rb', 'go', 'rs', 'ts'}

def is_allowed_file(filename: str) -> bool:
    """Check if a file has an allowed extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in get_allowed_file_extensions()

def save_uploaded_file(file, directory: Optional[str] = None) -> str:
    """
    Save an uploaded file to the upload directory.
    
    Args:
        file: File from request.files
        directory: Optional subdirectory within upload folder
        
    Returns:
        Path to the saved file
    """
    filename = secure_filename(file.filename)
    unique_filename = f"{time.time()}_{filename}"
    
    upload_dir = current_app.config['UPLOAD_FOLDER']
    if directory:
        upload_dir = os.path.join(upload_dir, directory)
        os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    return file_path

def json_response(data: Any, status_code: int = 200) -> tuple:
    """
    Create a JSON response with the given data and status code.
    
    Args:
        data: Data to be converted to JSON
        status_code: HTTP status code
        
    Returns:
        Flask response tuple with JSON data and status code
    """
    return jsonify(data), status_code

def error_response(message: str, status_code: int = 400) -> tuple:
    """
    Create an error response with the given message and status code.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        Flask response tuple with error message and status code
    """
    return jsonify({'error': message}), status_code

def start_execution_timer():
    """
    Initialize the global execution timer for a request.
    Should be called at the beginning of a request.
    """
    # Initialize execution_times if it doesn't exist
    if not hasattr(g, 'execution_times'):
        g.execution_times = {}
    
    # Record start time
    g.execution_times['start_time'] = time.time()

def measure_execution_time(func: Callable) -> Callable:
    """
    Decorator to measure and log function execution time.
    
    Args:
        func: The function to measure
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.debug(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
        
        # Initialize execution_times if it doesn't exist
        if not hasattr(g, 'execution_times'):
            g.execution_times = {}
            
        g.execution_times[func.__name__] = execution_time
            
        return result
    return wrapper

def validate_path(path: str) -> bool:
    """
    Validate that a path exists and is accessible.
    
    Args:
        path: Path to validate
        
    Returns:
        True if path exists and is accessible, False otherwise
    """
    try:
        return os.path.exists(path) and os.access(path, os.R_OK)
    except:
        return False

def document_api(
    summary: str,
    description: str = None,
    tags: List[str] = None,
    parameters: List[Dict[str, Any]] = None,
    request_body: Dict[str, Any] = None,
    responses: Dict[str, Dict[str, Any]] = None,
    security: List[Dict[str, List[str]]] = None,
    deprecated: bool = False
) -> Callable:
    """
    Decorator to document API endpoints for OpenAPI specification.
    
    Args:
        summary: Short summary of the endpoint
        description: Detailed description of the endpoint
        tags: List of tags for categorizing the endpoint
        parameters: List of parameter descriptions
        request_body: Description of request body
        responses: Dictionary of possible responses
        security: List of security requirements
        deprecated: Whether the endpoint is deprecated
        
    Returns:
        Decorated function with OpenAPI documentation
    """
    def decorator(func: Callable) -> Callable:
        # Set default values
        if description is None and func.__doc__:
            desc = func.__doc__.strip()
        else:
            desc = description or summary
            
        doc_tags = tags or []
        doc_parameters = parameters or []
        doc_responses = responses or {
            "200": {
                "description": "Successful response",
                "content": {"application/json": {}}
            },
            "400": {
                "description": "Bad request",
                "content": {"application/json": {"schema": {"type": "object", "properties": {"error": {"type": "string"}}}}}
            },
            "401": {
                "description": "Unauthorized",
                "content": {"application/json": {"schema": {"type": "object", "properties": {"error": {"type": "string"}}}}}
            },
            "500": {
                "description": "Internal server error",
                "content": {"application/json": {"schema": {"type": "object", "properties": {"error": {"type": "string"}}}}}
            }
        }
        doc_security = security or [{"bearerAuth": []}]
            
        # Build OpenAPI documentation
        openapi = {
            "summary": summary,
            "description": desc,
            "tags": doc_tags,
            "parameters": doc_parameters,
            "responses": doc_responses,
            "deprecated": deprecated
        }
        
        # Add request body if provided
        if request_body:
            openapi["requestBody"] = request_body
            
        # Add security requirements if provided
        if doc_security:
            openapi["security"] = doc_security
            
        # Store the OpenAPI documentation in the function
        func.__apispec__ = openapi
        
        return func
    return decorator 