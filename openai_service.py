import json
import os
import logging
from typing import Dict, List, Any, Optional

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
from openai import OpenAI

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def get_health_tips(user: Dict, profile: Dict, recent_logs: List[Dict], weather_data: Dict) -> List[str]:
    """Get personalized health tips using AI or fallback rules"""
    
    if not openai_client:
        logger.warning("OpenAI API key not available, using fallback tips")
        return get_fallback_health_tips(user, profile, recent_logs, weather_data)
    
    try:
        # Prepare context for AI
        context = prepare_health_context(user, profile, recent_logs, weather_data)
        
        prompt = f"""Based on the following user health data, provide 3-5 personalized health tips. 
        Respond with a JSON object containing an array of tips.

        User Context:
        {context}

        Please provide actionable, specific health tips considering:
        1. Sleep patterns and quality
        2. Exercise habits and frequency
        3. Nutrition and hydration
        4. Weather conditions and environmental factors
        5. Overall wellness and preventive care

        Respond in JSON format: {{"tips": ["tip1", "tip2", "tip3"]}}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a healthcare expert providing personalized wellness advice. "
                               "Focus on preventive care, lifestyle improvements, and actionable recommendations."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
            return result.get('tips', get_fallback_health_tips(user, profile, recent_logs, weather_data))
        else:
            return get_fallback_health_tips(user, profile, recent_logs, weather_data)
        
    except Exception as e:
        logger.error(f"AI health tips error: {str(e)}")
        return get_fallback_health_tips(user, profile, recent_logs, weather_data)

def chat_with_ai(message: str, user: Dict, profile: Dict, recent_logs: List[Dict]) -> str:
    """Chat with AI health assistant"""
    
    if not openai_client:
        logger.warning("OpenAI API key not available, using fallback response")
        return get_fallback_chat_response(message)
    
    try:
        context = prepare_health_context(user, profile, recent_logs, {})
        
        system_prompt = f"""You are a helpful healthcare assistant. You have access to the user's health profile:
        
        {context}
        
        Provide helpful, accurate health advice while being supportive and encouraging. 
        Always remind users to consult healthcare professionals for serious concerns.
        Keep responses concise and actionable."""
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=300
        )
        
        return response.choices[0].message.content or "I'm sorry, I couldn't generate a response. Please try again."
        
    except Exception as e:
        logger.error(f"AI chat error: {str(e)}")
        return get_fallback_chat_response(message)

def prepare_health_context(user: Dict, profile: Dict, recent_logs: List[Dict], weather_data: Dict) -> str:
    """Prepare user context for AI requests"""
    
    context_parts = []
    
    # User basic info
    if user:
        context_parts.append(f"User: {user.get('name', 'N/A')}, Premium: {user.get('is_premium', False)}")
    
    # Profile information
    if profile:
        context_parts.append(f"Age: {profile.get('age', 'N/A')}")
        context_parts.append(f"Gender: {profile.get('gender', 'N/A')}")
        context_parts.append(f"Location: {profile.get('location', 'N/A')}")
        context_parts.append(f"Exercise Frequency: {profile.get('exercise_frequency', 'N/A')}")
        context_parts.append(f"Target Sleep Hours: {profile.get('sleep_hours', 'N/A')}")
        context_parts.append(f"Diet Type: {profile.get('diet_type', 'N/A')}")
    
    # Recent lifestyle data
    if recent_logs:
        context_parts.append("\nRecent Lifestyle Logs:")
        for log in recent_logs[:3]:  # Last 3 entries
            context_parts.append(f"Date: {log['date']} - Sleep: {log['sleep_hours']}h, "
                                f"Exercise: {log['exercise_minutes']}min, Water: {log['water_glasses']} glasses")
    
    # Weather context
    if weather_data and 'current' in weather_data:
        current = weather_data['current']
        context_parts.append(f"\nCurrent Weather: {current.get('description', 'N/A')}, "
                           f"Temp: {current.get('temp', 'N/A')}°C, "
                           f"Humidity: {current.get('humidity', 'N/A')}%")
    
    return "\n".join(context_parts)

def get_fallback_health_tips(user: Dict, profile: Dict, recent_logs: List[Dict], weather_data: Dict) -> List[str]:
    """Fallback rule-based health tips when AI is unavailable"""
    
    tips = []
    
    # Sleep tips
    if recent_logs:
        avg_sleep = sum(log['sleep_hours'] for log in recent_logs[:7]) / min(len(recent_logs), 7)
        if avg_sleep < 7:
            tips.append("💤 Try to get 7-9 hours of sleep nightly for better health and immunity.")
        elif avg_sleep > 9:
            tips.append("💤 Consider maintaining a consistent sleep schedule - too much sleep can also affect energy levels.")
    else:
        tips.append("💤 Maintain a regular sleep schedule of 7-9 hours for optimal health.")
    
    # Exercise tips
    if recent_logs:
        avg_exercise = sum(log['exercise_minutes'] for log in recent_logs[:7]) / min(len(recent_logs), 7)
        if avg_exercise < 30:
            tips.append("🏃‍♂️ Aim for at least 30 minutes of physical activity daily to boost your cardiovascular health.")
    else:
        tips.append("🏃‍♂️ Regular exercise is key to maintaining good health - aim for 150 minutes per week.")
    
    # Hydration tips
    if recent_logs:
        avg_water = sum(log['water_glasses'] for log in recent_logs[:7]) / min(len(recent_logs), 7)
        if avg_water < 8:
            tips.append("💧 Stay hydrated by drinking at least 8 glasses of water daily.")
    else:
        tips.append("💧 Proper hydration is essential - aim for 8-10 glasses of water daily.")
    
    # Weather-based tips
    if weather_data and 'current' in weather_data:
        temp = weather_data['current'].get('temp', 25)
        humidity = weather_data['current'].get('humidity', 50)
        
        if temp > 30:
            tips.append("☀️ High temperatures detected - stay cool, drink extra water, and avoid outdoor activities during peak hours.")
        elif temp < 15:
            tips.append("❄️ Cool weather - dress warmly and maintain your immune system with proper nutrition.")
        
        if humidity > 80:
            tips.append("💨 High humidity levels - be aware of increased risk of heat-related stress and dehydration.")
    
    # General wellness tips
    tips.extend([
        "🥗 Include plenty of fruits and vegetables in your diet for essential vitamins and minerals.",
        "🧘‍♀️ Practice stress management techniques like meditation or deep breathing exercises.",
        "👩‍⚕️ Schedule regular health check-ups and screenings for preventive care."
    ])
    
    return tips[:5]  # Return top 5 tips

def get_fallback_chat_response(message: str) -> str:
    """Fallback chat responses when AI is unavailable"""
    
    message_lower = message.lower()
    
    # Health-related keywords and responses
    if any(word in message_lower for word in ['sleep', 'tired', 'insomnia']):
        return "For better sleep, try maintaining a consistent bedtime routine, avoiding screens before bed, and creating a comfortable sleep environment. If sleep issues persist, consider consulting a healthcare professional."
    
    elif any(word in message_lower for word in ['exercise', 'workout', 'fitness']):
        return "Regular exercise is great for overall health! Start with activities you enjoy, aim for at least 30 minutes daily, and gradually increase intensity. Always consult a doctor before starting a new exercise program."
    
    elif any(word in message_lower for word in ['diet', 'nutrition', 'food', 'eating']):
        return "A balanced diet with plenty of fruits, vegetables, whole grains, and lean proteins supports good health. Stay hydrated and limit processed foods. Consider consulting a nutritionist for personalized advice."
    
    elif any(word in message_lower for word in ['stress', 'anxiety', 'mental']):
        return "Managing stress is important for overall health. Try relaxation techniques like deep breathing, meditation, or regular exercise. Don't hesitate to reach out to mental health professionals if needed."
    
    elif any(word in message_lower for word in ['water', 'hydration', 'drink']):
        return "Staying hydrated is essential! Aim for 8-10 glasses of water daily, more if you're active or in hot weather. Water helps with digestion, circulation, and temperature regulation."
    
    else:
        return "I'm here to help with your health and wellness questions! For specific medical concerns, please consult with a healthcare professional. Is there a particular aspect of your health you'd like to discuss?"
