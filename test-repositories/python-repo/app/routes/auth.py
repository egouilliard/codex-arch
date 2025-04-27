from flask import Blueprint, request, jsonify, session
from ..models.user import User, Profile
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils.validators import validate_email, validate_password
from ..services.email import send_welcome_email, send_password_reset
import jwt
import datetime
import os

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request body:
        email (str): User email
        username (str): User username
        password (str): User password
        
    Returns:
        JSON: Success message and user ID
    """
    data = request.get_json()
    
    # Validate the input
    if not all(k in data for k in ('email', 'username', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Check if email is valid
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
        
    # Check if password is strong enough
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 8 characters and contain a number and a special character'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
        
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    # Create a new user
    new_user = User(
        email=data['email'],
        username=data['username']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    # Create user profile
    profile = Profile(user_id=new_user.id)
    db.session.add(profile)
    db.session.commit()
    
    # Send welcome email
    send_welcome_email(new_user.email, new_user.username)
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': new_user.id
    }), 201


@auth.route('/login', methods=['POST'])
def login():
    """
    Log in a user
    
    Request body:
        email (str): User email
        password (str): User password
        
    Returns:
        JSON: Success message and JWT token
    """
    data = request.get_json()
    
    if not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, os.environ.get('SECRET_KEY', 'dev_key'), algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user_id': user.id
    }), 200


@auth.route('/logout', methods=['POST'])
def logout():
    """
    Log out a user
    
    Returns:
        JSON: Success message
    """
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@auth.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Send password reset email
    
    Request body:
        email (str): User email
        
    Returns:
        JSON: Success message
    """
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        # Don't reveal that the user doesn't exist
        return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
    
    # Generate reset token
    reset_token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, os.environ.get('SECRET_KEY', 'dev_key'), algorithm='HS256')
    
    # Send password reset email
    send_password_reset(user.email, reset_token)
    
    return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200 