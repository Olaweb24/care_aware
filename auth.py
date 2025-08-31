from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging

from models import User, Profile

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'age', 'gender', 'location', 
                          'exercise_frequency', 'sleep_hours', 'diet_type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        if User.get_by_email(data['email']):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        password_hash = generate_password_hash(data['password'])
        user_id = User.create(data['name'], data['email'], password_hash)
        
        # Create profile
        Profile.create_or_update(
            user_id=user_id,
            age=int(data['age']),
            gender=data['gender'],
            location=data['location'],
            exercise_frequency=data['exercise_frequency'],
            sleep_hours=float(data['sleep_hours']),
            diet_type=data['diet_type']
        )
        
        # Log in user
        session['user_id'] = user_id
        session['user_email'] = data['email']
        
        logger.info(f"User registered successfully: {data['email']}")
        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.get_by_email(data['email'])
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Log in user
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        
        logger.info(f"User logged in successfully: {data['email']}")
        return jsonify({'message': 'Login successful', 'user_id': user['id']}), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/profile', methods=['GET'])
@require_login
def get_profile():
    try:
        user_id = session['user_id']
        user = User.get_by_id(user_id)
        profile = Profile.get_by_user_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Remove sensitive data
        user_data = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'created_at': user['created_at'],
            'is_premium': user['is_premium']
        }
        
        return jsonify({'user': user_data, 'profile': profile}), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_login
def update_profile():
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        # Update profile
        Profile.create_or_update(
            user_id=user_id,
            age=int(data.get('age', 25)),
            gender=data.get('gender', 'other'),
            location=data.get('location', ''),
            exercise_frequency=data.get('exercise_frequency', 'moderate'),
            sleep_hours=float(data.get('sleep_hours', 8)),
            diet_type=data.get('diet_type', 'balanced')
        )
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500
