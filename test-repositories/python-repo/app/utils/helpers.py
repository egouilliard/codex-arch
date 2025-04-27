import os
import jwt
from functools import wraps
from flask import request, jsonify, render_template
from ..models.user import User
import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)

def token_required(f):
    """
    Decorator to require JWT token for route
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected(current_user):
            return jsonify({'message': f'Hello {current_user.username}'})
    
    Returns:
        function: Decorated function with current_user passed as first argument
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            # Decode token
            data = jwt.decode(
                token, 
                os.environ.get('SECRET_KEY', 'dev_key'), 
                algorithms=['HS256']
            )
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                raise Exception("User not found")
                
            # Check if token is expired
            if 'exp' in data and datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(data['exp']):
                raise Exception("Token has expired")
                
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({'error': 'Token is invalid'}), 401
            
        # Pass the current user to the route
        return f(current_user, *args, **kwargs)
        
    return decorated

def admin_required(f):
    """
    Decorator to require admin role for route
    
    Usage:
        @app.route('/admin-only')
        @token_required
        @admin_required
        def admin_only(current_user):
            return jsonify({'message': 'Hello admin'})
    
    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Admin privileges required'}), 403
            
        return f(current_user, *args, **kwargs)
        
    return decorated

def format_email_template(template_name, template_data):
    """
    Format an email template with data
    
    Args:
        template_name (str): Name of the template file
        template_data (dict): Data to render in the template
        
    Returns:
        str: Formatted template content
    """
    try:
        # In a real app, use render_template from Flask to load from templates directory
        # Here we'll simulate it with a simple string template
        
        templates = {
            'welcome.html': """
                <h1>Welcome to Our Flask App, {username}!</h1>
                <p>Thank you for joining our community. We're excited to have you on board.</p>
                <p>You can <a href="{login_url}">login here</a> to get started.</p>
                <p>If you have any questions, please contact <a href="mailto:{support_email}">{support_email}</a>.</p>
            """,
            'welcome.txt': """
                Welcome to Our Flask App, {username}!
                
                Thank you for joining our community. We're excited to have you on board.
                
                You can login here: {login_url}
                
                If you have any questions, please contact {support_email}.
            """,
            'password_reset.html': """
                <h1>Password Reset Request</h1>
                <p>We received a request to reset your password. Click the link below to reset it:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link will expire in {expires_in}.</p>
                <p>If you didn't request this, please ignore this email or contact <a href="mailto:{support_email}">{support_email}</a>.</p>
            """,
            'password_reset.txt': """
                Password Reset Request
                
                We received a request to reset your password. Copy and paste the link below to reset it:
                
                {reset_url}
                
                This link will expire in {expires_in}.
                
                If you didn't request this, please ignore this email or contact {support_email}.
            """
        }
        
        if template_name not in templates:
            logger.error(f"Template {template_name} not found")
            return f"Template {template_name} not found"
            
        # Format the template with the provided data
        return templates[template_name].format(**template_data)
        
    except Exception as e:
        logger.error(f"Error formatting email template: {str(e)}")
        return "Error formatting email template"

def paginate(query, page, per_page, error_out=True):
    """
    Helper function to paginate query results
    
    Args:
        query: SQLAlchemy query
        page (int): Page number
        per_page (int): Items per page
        error_out (bool): Whether to raise 404 if page is out of range
        
    Returns:
        dict: Pagination object with items, page info, etc.
    """
    pagination = query.paginate(page=page, per_page=per_page, error_out=error_out)
    
    return {
        'items': pagination.items,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'next_num': pagination.next_num,
        'prev_num': pagination.prev_num
    } 