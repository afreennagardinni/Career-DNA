"""
Authentication Routes
Handles user registration, login, logout, and session management.
"""

from flask import Blueprint, request, jsonify, session, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET'])
def register_page():
    """
    Render the registration page.
    
    Returns:
        Rendered HTML template
    """
    return render_template('register.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "username": "johndoe",
        "password": "securepassword",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    Returns:
        JSON response with user data or error message
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ['email', 'password', 'first_name', 'last_name']):
        return jsonify({
            'error': 'Missing required fields',
            'message': 'email, password, first_name, and last_name are required'
        }), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email already registered',
            'message': 'An account with this email already exists'
        }), 409
    
    # Create username from email if not provided
    username = data.get('username', data['email'].split('@')[0])
    
    # Ensure username is unique
    original_username = username
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f"{original_username}{counter}"
        counter += 1
    
    # Create new user
    user = User(
        email=data['email'],
        username=username,
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    user.set_password(data['password'])
    
    try:
        user.save()
        
        # Create empty profile for the user
        profile = Profile(user_id=user.id)
        profile.save()
        
        # Log in the user automatically after registration
        login_user(user)
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """
    Render the login page.
    
    Returns:
        Rendered HTML template
    """
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in an existing user.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    
    Returns:
        JSON response with user data or error message
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({
            'error': 'Missing credentials',
            'message': 'email and password are required'
        }), 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    # Check if user exists and password is correct
    if not user or not user.check_password(data['password']):
        return jsonify({
            'error': 'Invalid credentials',
            'message': 'Invalid email or password'
        }), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({
            'error': 'Account inactive',
            'message': 'Your account has been deactivated'
        }), 403
    
    # Log in the user
    login_user(user)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    Log out the current user.
    
    Returns:
        JSON response confirming logout
    """
    logout_user()
    return jsonify({
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get the current authenticated user's information.
    
    Returns:
        JSON response with user data
    """
    return jsonify({
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['PUT'])
@login_required
def update_current_user():
    """
    Update the current authenticated user's information.
    
    Expected JSON payload (all fields optional):
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "newemail@example.com"
    }
    
    Returns:
        JSON response with updated user data
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'No data provided',
            'message': 'No update data provided'
        }), 400
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'email']
    
    for field in allowed_fields:
        if field in data:
            # Check if email is being changed and if it's already taken
            if field == 'email' and data[field] != current_user.email:
                if User.query.filter_by(email=data[field]).first():
                    return jsonify({
                        'error': 'Email already in use',
                        'message': 'This email is already registered to another account'
                    }), 409
            setattr(current_user, field, data[field])
    
    try:
        current_user.save()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Update failed',
            'message': str(e)
        }), 500
