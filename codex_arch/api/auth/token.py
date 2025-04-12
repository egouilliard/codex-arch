"""
JWT token authentication for the Codex-Arch API.

This module provides functionality for JWT token generation, validation, and
authorization decorators for securing API endpoints.
"""

import os
import jwt
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, Callable
from flask import request, jsonify, current_app, g

logger = logging.getLogger(__name__)

def generate_token(user_id: str, is_admin: bool = False, expiration: Optional[int] = None) -> str:
    """
    Generate a JWT token for the given user.
    
    Args:
        user_id: User identifier
        is_admin: Whether the user has admin privileges
        expiration: Token expiration time in seconds (defaults to config value)
        
    Returns:
        JWT token as string
    """
    try:
        # Get expiration time from config if not provided
        exp_seconds = expiration or current_app.config.get('JWT_EXPIRATION', 3600)  # Default 1 hour
        
        # Create payload
        payload = {
            'user_id': user_id,
            'is_admin': is_admin,
            'exp': datetime.utcnow() + timedelta(seconds=exp_seconds),
            'iat': datetime.utcnow()
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
        
        return token
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}", exc_info=True)
        raise

def validate_token(token: str) -> Dict[str, Any]:
    """
    Validate a JWT token and return the payload.
    
    Args:
        token: JWT token to validate
        
    Returns:
        Token payload as dictionary
        
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        # Decode token
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=['HS256']
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise ValueError("Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}", exc_info=True)
        raise ValueError(f"Error validating token: {str(e)}")

def token_required(f: Callable) -> Callable:
    """
    Decorator for routes that require token authentication.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # Check format: "Bearer <token>"
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
                
        # Token required
        if not token:
            return jsonify({
                'success': False,
                'error': 'Missing authentication token'
            }), 401
            
        try:
            # Validate token and set payload in g (flask's application context)
            payload = validate_token(token)
            g.user = payload
            
            # Pass to wrapped function
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 401
            
    return decorated

def admin_required(f: Callable) -> Callable:
    """
    Decorator for routes that require admin privileges.
    Must be used with token_required decorator.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if user exists and is admin
        if not hasattr(g, 'user'):
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
            
        if not g.user.get('is_admin', False):
            return jsonify({
                'success': False,
                'error': 'Admin privileges required'
            }), 403
            
        # Pass to wrapped function
        return f(*args, **kwargs)
            
    return decorated 