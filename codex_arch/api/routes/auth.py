"""
Authentication routes for the Codex-Arch REST API.

These routes handle user authentication and token management.
"""

import os
import logging
import json
import hashlib
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app, g

from codex_arch.api.auth import generate_token, validate_token, token_required, admin_required
from codex_arch.api.utils import json_response, error_response, measure_execution_time

# Create blueprint
bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Simple user store for development purposes
# In production, this would be replaced with a proper database
USERS = {
    # Default admin user (username: admin, password: adminpass)
    'admin': {
        'password_hash': hashlib.sha256('adminpass'.encode()).hexdigest(),
        'is_admin': True
    },
    # Default regular user (username: user, password: userpass)
    'user': {
        'password_hash': hashlib.sha256('userpass'.encode()).hexdigest(),
        'is_admin': False
    }
}

@bp.route('/login', methods=['POST'])
@measure_execution_time
def login():
    """
    Handle user login and generate JWT token.
    
    Request body:
        username: User's username
        password: User's password
    
    Returns:
        JSON with token on success, error message on failure
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return error_response("Missing request data", 400)
            
        username = data.get('username')
        password = data.get('password')
        
        # Validate input
        if not username or not password:
            return error_response("Username and password are required", 400)
            
        # Check if user exists
        user = USERS.get(username)
        if not user:
            return error_response("Invalid username or password", 401)
            
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user['password_hash']:
            return error_response("Invalid username or password", 401)
            
        # Generate token
        token = generate_token(username, user['is_admin'])
        
        # Return response
        return json_response({
            'success': True,
            'token': token,
            'user': {
                'username': username,
                'is_admin': user['is_admin']
            }
        })
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        return error_response(f"Login failed: {str(e)}", 500)

@bp.route('/validate', methods=['GET'])
@token_required
@measure_execution_time
def validate():
    """
    Validate a token and return user info.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        User information from token payload
    """
    try:
        # User info is set in g.user by token_required decorator
        return json_response({
            'success': True,
            'user': {
                'username': g.user['user_id'],
                'is_admin': g.user['is_admin']
            }
        })
        
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}", exc_info=True)
        return error_response(f"Token validation failed: {str(e)}", 500)

@bp.route('/admin-only', methods=['GET'])
@token_required
@admin_required
@measure_execution_time
def admin_only():
    """
    Example endpoint that requires admin privileges.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        Success message for admin users
    """
    return json_response({
        'success': True,
        'message': 'You have admin privileges'
    })

@bp.route('/refresh', methods=['POST'])
@token_required
@measure_execution_time
def refresh_token():
    """
    Refresh a valid token to extend its expiration.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        New token with extended expiration
    """
    try:
        # User info is set in g.user by token_required decorator
        new_token = generate_token(g.user['user_id'], g.user['is_admin'])
        
        return json_response({
            'success': True,
            'token': new_token
        })
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}", exc_info=True)
        return error_response(f"Token refresh failed: {str(e)}", 500) 