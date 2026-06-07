"""
Authentication Routes
Handles user registration, login, logout, and session management.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile

# Create blueprint with correct configuration
auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET'])
def register_page():
    """
    Render registration page.
    
    Returns:
        Rendered HTML template
    """
    print("DEBUG: GET /auth/register route hit")
    return render_template('register.html')


@auth.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "securepassword",
        "confirm_password": "securepassword"
    }
    
    Returns:
        JSON response with user data or error message
    """
    print("DEBUG: POST /auth/register route hit")
    
    # Check if this is JSON (API) or form (HTML) submission
    if request.is_json:
        data = request.get_json()
        print(f"DEBUG: JSON data received: {data}")
    else:
        data = request.form.to_dict()
        print(f"DEBUG: Form data received: {data}")
    
    # Validate required fields - handle form field names with hyphens
    if not data:
        error_msg = 'No data received'
        print(f"DEBUG: Validation error - {error_msg}")
        
        if request.is_json:
            return jsonify({
                'error': 'No data received',
                'message': error_msg
            }), 400
        else:
            return render_template('register.html', error=error_msg)
    
    # Map form field names to expected names
    email = data.get('email') or data.get('email', '')
    password = data.get('password') or data.get('password', '')
    first_name = data.get('first-name') or data.get('first_name', '')
    last_name = data.get('last-name') or data.get('last_name', '')
    
    if not all([email, password, first_name, last_name]):
        error_msg = 'Missing required fields: email, password, first_name, and last_name are required'
        print(f"DEBUG: Validation error - {error_msg}")
        print(f"DEBUG: Field values - email: {email}, password: {bool(password)}, first_name: {first_name}, last_name: {last_name}")
        
        if request.is_json:
            return jsonify({
                'error': 'Missing required fields',
                'message': error_msg
            }), 400
        else:
            return render_template('register.html', error=error_msg)
    
    # Validate passwords match
    confirm_password = data.get('confirm_password') or data.get('confirm-password', '')
    if password != confirm_password:
        error_msg = 'Passwords do not match'
        print(f"DEBUG: Password mismatch error - {error_msg}")
        
        if request.is_json:
            return jsonify({
                'error': 'Passwords do not match',
                'message': error_msg
            }), 400
        else:
            return render_template('register.html', error=error_msg)
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        error_msg = 'An account with this email already exists'
        print(f"DEBUG: User already exists - {error_msg}")
        
        if request.is_json:
            return jsonify({
                'error': 'Email already registered',
                'message': error_msg
            }), 409
        else:
            return render_template('register.html', error=error_msg)
    
    # Create username from email
    username = data['email'].split('@')[0]
    
    # Ensure username is unique
    original_username = username
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f"{original_username}{counter}"
        counter += 1
    
    # Create new user
    user = User(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    user.set_password(password)
    
    try:
        user.save()
        print(f"DEBUG: User created successfully - {user.email}")
        
        # Create empty profile for the user
        profile = Profile(user_id=user.id)
        profile.save()
        print("DEBUG: Profile created successfully")
        
        # Log in user automatically after registration
        login_user(user)
        print("DEBUG: User logged in successfully")
        
        success_msg = 'Registration successful'
        
        if request.is_json:
            return jsonify({
                'message': success_msg,
                'user': user.to_dict()
            }), 201
        else:
            # For form submission, redirect to dashboard
            return render_template('register.html', success=success_msg)
    
    except Exception as e:
        print(f"DEBUG: Registration failed - {str(e)}")
        db.session.rollback()
        
        error_msg = f'Registration failed: {str(e)}'
        
        if request.is_json:
            return jsonify({
                'error': 'Registration failed',
                'message': error_msg
            }), 500
        else:
            return render_template('register.html', error=error_msg)


@auth.route('/login', methods=['GET'])
def login_page():
    """
    Render login page.
    
    Returns:
        Rendered HTML template
    """
    print("DEBUG: GET /auth/login route hit")
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
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
    print("DEBUG: POST /auth/login route hit")
    
    # Check if this is JSON (API) or form (HTML) submission
    if request.is_json:
        data = request.get_json()
        print(f"DEBUG: JSON data received: {data}")
    else:
        data = request.form.to_dict()
        print(f"DEBUG: Form data received: {data}")
    
    # Validate required fields
    if not data or not all(k in data for k in ['email', 'password']):
        error_msg = 'email and password are required'
        print(f"DEBUG: Validation error - {error_msg}")
        
        if request.is_json:
            return jsonify({
                'error': 'Missing credentials',
                'message': error_msg
            }), 400
        else:
            return render_template('login.html', error=error_msg)
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    # Check if user exists and password is correct
    if not user or not user.check_password(data['password']):
        error_msg = 'Invalid email or password'
        print(f"DEBUG: Invalid credentials - {error_msg}")
        
        if request.is_json:
            return jsonify({
                'error': 'Invalid credentials',
                'message': error_msg
            }), 401
        else:
            return render_template('login.html', error=error_msg)
    
    # Check if user is active
    if not user.is_active:
        error_msg = 'Your account has been deactivated'
        print(f"DEBUG: Account inactive - {error_msg}")
        
        if request.is_json:
            return jsonify({
                'error': 'Account inactive',
                'message': error_msg
            }), 403
        else:
            return render_template('login.html', error=error_msg)
    
    # Log in user
    login_user(user)
    print(f"DEBUG: User logged in successfully - {user.email}")
    
    success_msg = 'Login successful'
    
    if request.is_json:
        return jsonify({
            'message': success_msg,
            'user': user.to_dict()
        }), 200
    else:
        # For form submission, redirect to dashboard
        return render_template('login.html', success=success_msg)


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Log out the current user.
    
    Returns:
        JSON response confirming logout
    """
    print("DEBUG: POST /auth/logout route hit")
    logout_user()
    
    if request.is_json:
        return jsonify({
            'message': 'Logout successful'
        }), 200
    else:
        # For form submission, redirect to login
        return render_template('login.html', success='Logout successful')


@auth.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get the current authenticated user's information.
    
    Returns:
        JSON response with user data
    """
    print("DEBUG: GET /auth/api/me route hit")
    return jsonify({
        'user': current_user.to_dict()
    }), 200
