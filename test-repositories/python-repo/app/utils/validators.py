import re
import string
from functools import wraps
from flask import request, jsonify

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_password(password):
    """
    Validate password strength
    
    Password must:
    - Be at least 8 characters long
    - Contain at least one digit
    - Contain at least one special character
    
    Args:
        password (str): Password to validate
        
    Returns:
        bool: True if password is valid, False otherwise
    """
    if len(password) < 8:
        return False
        
    if not any(c.isdigit() for c in password):
        return False
        
    special_chars = set(string.punctuation)
    if not any(c in special_chars for c in password):
        return False
        
    return True

def validate_username(username):
    """
    Validate username format
    
    Username must:
    - Be 3-20 characters long
    - Contain only alphanumeric characters, underscores, or hyphens
    - Start with a letter
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if username is valid, False otherwise
    """
    username_pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{2,19}$'
    return bool(re.match(username_pattern, username))

def validate_post_content(content):
    """
    Validate post content
    
    Content must:
    - Not be empty
    - Be at most 5000 characters long
    
    Args:
        content (str): Content to validate
        
    Returns:
        bool: True if content is valid, False otherwise
    """
    return bool(content) and len(content) <= 5000

def validate_request_json(*required_fields):
    """
    Decorator to validate request JSON
    
    Args:
        *required_fields: Required fields in request JSON
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
                
            data = request.get_json()
            
            # Check if all required fields are present
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f"Missing required fields: {', '.join(missing_fields)}"
                }), 400
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator 