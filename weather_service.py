import os
import requests
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'

def get_weather_data(location: str) -> Optional[Dict[str, Any]]:
    """Get weather data for a location"""
    
    if not OPENWEATHER_API_KEY:
        logger.warning("OpenWeather API key not available, using mock weather data")
        return get_mock_weather_data(location)
    
    try:
        # Get current weather
        current_url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            'q': location,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(current_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            weather_info = {
                'location': data['name'],
                'country': data['sys']['country'],
                'current': {
                    'temp': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': data.get('wind', {}).get('speed', 0),
                    'visibility': data.get('visibility', 10000) / 1000  # Convert to km
                },
                'risk_indicators': calculate_health_risks(data)
            }
            
            return weather_info
        else:
            logger.error(f"OpenWeather API error: {response.status_code} - {response.text}")
            return get_mock_weather_data(location)
            
    except Exception as e:
        logger.error(f"Weather service error: {str(e)}")
        return get_mock_weather_data(location)

def get_mock_weather_data(location: str) -> Dict[str, Any]:
    """Generate mock weather data when API is unavailable"""
    
    return {
        'location': location,
        'country': 'NG',
        'current': {
            'temp': 28,
            'feels_like': 32,
            'humidity': 75,
            'pressure': 1013,
            'description': 'Partly Cloudy',
            'icon': '02d',
            'wind_speed': 2.5,
            'visibility': 10
        },
        'risk_indicators': {
            'heat_stress': 'moderate',
            'uv_risk': 'high',
            'air_quality': 'moderate',
            'dehydration_risk': 'moderate'
        },
        'mock_data': True
    }

def calculate_health_risks(weather_data: Dict) -> Dict[str, str]:
    """Calculate health risk indicators based on weather data"""
    
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    feels_like = weather_data['main']['feels_like']
    
    risks = {}
    
    # Heat stress risk
    if feels_like > 35:
        risks['heat_stress'] = 'high'
    elif feels_like > 30:
        risks['heat_stress'] = 'moderate'
    else:
        risks['heat_stress'] = 'low'
    
    # UV risk (simplified based on time and weather)
    weather_main = weather_data['weather'][0]['main'].lower()
    if 'clear' in weather_main and temp > 25:
        risks['uv_risk'] = 'high'
    elif temp > 20:
        risks['uv_risk'] = 'moderate'
    else:
        risks['uv_risk'] = 'low'
    
    # Air quality risk (simplified)
    if humidity > 80:
        risks['air_quality'] = 'poor'
    elif humidity > 60:
        risks['air_quality'] = 'moderate'
    else:
        risks['air_quality'] = 'good'
    
    # Dehydration risk
    if temp > 32 or (temp > 28 and humidity > 70):
        risks['dehydration_risk'] = 'high'
    elif temp > 25:
        risks['dehydration_risk'] = 'moderate'
    else:
        risks['dehydration_risk'] = 'low'
    
    return risks

def get_health_alerts(user: Dict, profile: Dict, recent_logs: List[Dict], weather_data: Dict) -> List[Dict[str, str]]:
    """Generate health alerts based on weather and user data"""
    
    alerts = []
    
    if not weather_data:
        return alerts
    
    current = weather_data.get('current', {})
    risks = weather_data.get('risk_indicators', {})
    
    # Temperature-based alerts
    temp = current.get('temp', 25)
    humidity = current.get('humidity', 50)
    
    if temp > 35:
        alerts.append({
            'type': 'warning',
            'title': 'Extreme Heat Alert',
            'message': 'Very high temperatures detected. Stay indoors, drink plenty of water, and avoid strenuous outdoor activities.',
            'icon': '🌡️'
        })
    elif temp > 30:
        alerts.append({
            'type': 'caution',
            'title': 'Heat Advisory',
            'message': 'High temperatures today. Stay hydrated and take breaks if working outdoors.',
            'icon': '☀️'
        })
    
    # Humidity alerts
    if humidity > 85:
        alerts.append({
            'type': 'info',
            'title': 'High Humidity Alert',
            'message': 'Very humid conditions may affect breathing and increase heat stress. Stay cool and hydrated.',
            'icon': '💨'
        })
    
    # Dehydration risk
    if risks.get('dehydration_risk') == 'high':
        alerts.append({
            'type': 'warning',
            'title': 'Dehydration Risk',
            'message': 'Weather conditions increase dehydration risk. Drink water regularly, even if you don\'t feel thirsty.',
            'icon': '💧'
        })
    
    # UV risk alerts
    if risks.get('uv_risk') == 'high':
        alerts.append({
            'type': 'caution',
            'title': 'High UV Index',
            'message': 'Strong UV radiation today. Use sunscreen, wear protective clothing, and seek shade during peak hours.',
            'icon': '🧴'
        })
    
    # Air quality alerts
    if risks.get('air_quality') == 'poor':
        alerts.append({
            'type': 'caution',
            'title': 'Air Quality Advisory',
            'message': 'Poor air quality conditions. Consider limiting outdoor activities, especially if you have respiratory issues.',
            'icon': '😷'
        })
    
    # Activity-based alerts using recent logs
    if recent_logs:
        avg_exercise = sum(log['exercise_minutes'] for log in recent_logs[:3]) / min(len(recent_logs), 3)
        if avg_exercise > 60 and temp > 30:
            alerts.append({
                'type': 'info',
                'title': 'Exercise Adjustment',
                'message': 'Consider indoor workouts or exercising during cooler hours due to high temperatures.',
                'icon': '🏃‍♂️'
            })
    
    # Seasonal health reminders
    if temp < 20:
        alerts.append({
            'type': 'info',
            'title': 'Cool Weather Reminder',
            'message': 'Cooler temperatures - ensure adequate vitamin D intake and maintain your exercise routine.',
            'icon': '🧥'
        })
    
    return alerts
