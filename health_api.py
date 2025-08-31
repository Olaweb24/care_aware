from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import logging

from models import LifestyleLog, User, Profile
from auth import require_login
from openai_service import get_health_tips, chat_with_ai
from weather_service import get_weather_data, get_health_alerts

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

@health_bp.route('/log-lifestyle', methods=['POST'])
@require_login
def log_lifestyle():
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sleep_hours', 'exercise_minutes', 'water_glasses', 'meals']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create lifestyle log
        log_id = LifestyleLog.create(
            user_id=user_id,
            date=data.get('date', datetime.now().strftime('%Y-%m-%d')),
            sleep_hours=float(data['sleep_hours']),
            exercise_minutes=int(data['exercise_minutes']),
            water_glasses=int(data['water_glasses']),
            meals=data['meals'],
            notes=data.get('notes', '')
        )
        
        logger.info(f"Lifestyle log created for user {user_id}: {log_id}")
        return jsonify({'message': 'Lifestyle log saved successfully', 'log_id': log_id}), 201
        
    except Exception as e:
        logger.error(f"Log lifestyle error: {str(e)}")
        return jsonify({'error': 'Failed to save lifestyle log'}), 500

@health_bp.route('/lifestyle', methods=['GET'])
@require_login
def get_lifestyle():
    try:
        user_id = session['user_id']
        limit = request.args.get('limit', 30, type=int)
        
        logs = LifestyleLog.get_by_user_id(user_id, limit)
        
        return jsonify({'logs': logs}), 200
        
    except Exception as e:
        logger.error(f"Get lifestyle error: {str(e)}")
        return jsonify({'error': 'Failed to get lifestyle logs'}), 500

@health_bp.route('/lifestyle_chart_data', methods=['GET'])
@require_login
def get_lifestyle_chart_data():
    try:
        user_id = session['user_id']
        logs = LifestyleLog.get_by_user_id(user_id, 7)  # Last 7 days
        
        # Prepare chart data
        chart_data = {
            'labels': [],
            'sleep_data': [],
            'exercise_data': [],
            'water_data': []
        }
        
        # Sort by date and format for chart
        logs_sorted = sorted(logs, key=lambda x: x['date'])
        
        for log in logs_sorted:
            chart_data['labels'].append(log['date'])
            chart_data['sleep_data'].append(log['sleep_hours'])
            chart_data['exercise_data'].append(log['exercise_minutes'])
            chart_data['water_data'].append(log['water_glasses'])
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        logger.error(f"Get chart data error: {str(e)}")
        return jsonify({'error': 'Failed to get chart data'}), 500

@health_bp.route('/get-tips', methods=['POST'])
@require_login
def get_tips():
    try:
        user_id = session['user_id']
        user = User.get_by_id(user_id)
        profile = Profile.get_by_user_id(user_id)
        recent_logs = LifestyleLog.get_by_user_id(user_id, 7)
        
        # Get location for weather data
        location = profile.get('location', 'Lagos') if profile else 'Lagos'
        weather_data = get_weather_data(location)
        
        # Get AI-powered tips
        tips = get_health_tips(user, profile, recent_logs, weather_data or {})
        
        return jsonify({'tips': tips}), 200
        
    except Exception as e:
        logger.error(f"Get tips error: {str(e)}")
        return jsonify({'error': 'Failed to get health tips'}), 500

@health_bp.route('/chat', methods=['POST'])
@require_login
def chat():
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        user = User.get_by_id(user_id)
        profile = Profile.get_by_user_id(user_id)
        recent_logs = LifestyleLog.get_by_user_id(user_id, 3)
        
        # Get AI response
        response = chat_with_ai(data['message'], user, profile, recent_logs)
        
        return jsonify({'response': response}), 200
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Failed to get chat response'}), 500

@health_bp.route('/weather', methods=['GET'])
@require_login
def weather():
    try:
        location = request.args.get('location')
        if not location:
            # Get user's location from profile
            user_id = session['user_id']
            profile = Profile.get_by_user_id(user_id)
            location = profile.get('location', 'Lagos') if profile else 'Lagos'
        
        weather_data = get_weather_data(location)
        
        if not weather_data:
            return jsonify({'error': 'Failed to get weather data'}), 500
        
        return jsonify(weather_data), 200
        
    except Exception as e:
        logger.error(f"Weather error: {str(e)}")
        return jsonify({'error': 'Failed to get weather data'}), 500

@health_bp.route('/alerts', methods=['GET'])
@require_login
def alerts():
    try:
        user_id = session['user_id']
        user = User.get_by_id(user_id)
        profile = Profile.get_by_user_id(user_id)
        recent_logs = LifestyleLog.get_by_user_id(user_id, 3)
        
        # Get location for weather
        location = profile.get('location', 'Lagos') if profile else 'Lagos'
        weather_data = get_weather_data(location)
        
        # Get health alerts
        alerts = get_health_alerts(user, profile, recent_logs, weather_data or {})
        
        return jsonify({'alerts': alerts}), 200
        
    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        return jsonify({'error': 'Failed to get health alerts'}), 500
