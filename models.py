import os
from datetime import datetime
from typing import Dict, List, Any

# In-memory storage for MVP
users_db: Dict[int, Dict[str, Any]] = {}
profiles_db: Dict[int, Dict[str, Any]] = {}
lifestyle_logs_db: Dict[int, List[Dict[str, Any]]] = {}
payments_db: Dict[int, List[Dict[str, Any]]] = {}

# Auto-increment counters
user_id_counter = 1
log_id_counter = 1
payment_id_counter = 1

def init_storage():
    """Initialize storage with sample data if needed"""
    pass

def get_next_user_id():
    global user_id_counter
    current_id = user_id_counter
    user_id_counter += 1
    return current_id

def get_next_log_id():
    global log_id_counter
    current_id = log_id_counter
    log_id_counter += 1
    return current_id

def get_next_payment_id():
    global payment_id_counter
    current_id = payment_id_counter
    payment_id_counter += 1
    return current_id

class User:
    @staticmethod
    def create(name: str, email: str, password_hash: str) -> int:
        user_id = get_next_user_id()
        users_db[user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat(),
            'is_premium': False
        }
        return user_id
    
    @staticmethod
    def get_by_email(email: str) -> Dict[str, Any] | None:
        for user in users_db.values():
            if user['email'] == email:
                return user
        return None
    
    @staticmethod
    def get_by_id(user_id: int) -> Dict[str, Any] | None:
        return users_db.get(user_id)
    
    @staticmethod
    def update_premium_status(user_id: int, is_premium: bool):
        if user_id in users_db:
            users_db[user_id]['is_premium'] = is_premium

class Profile:
    @staticmethod
    def create_or_update(user_id: int, age: int, gender: str, location: str, 
                        exercise_frequency: str, sleep_hours: float, diet_type: str):
        profiles_db[user_id] = {
            'user_id': user_id,
            'age': age,
            'gender': gender,
            'location': location,
            'exercise_frequency': exercise_frequency,
            'sleep_hours': sleep_hours,
            'diet_type': diet_type,
            'updated_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def get_by_user_id(user_id: int) -> Dict[str, Any] | None:
        return profiles_db.get(user_id)

class LifestyleLog:
    @staticmethod
    def create(user_id: int, date: str, sleep_hours: float, exercise_minutes: int,
               water_glasses: int, meals: str, notes: str) -> int:
        log_id = get_next_log_id()
        
        if user_id not in lifestyle_logs_db:
            lifestyle_logs_db[user_id] = []
        
        lifestyle_logs_db[user_id].append({
            'id': log_id,
            'user_id': user_id,
            'date': date,
            'sleep_hours': sleep_hours,
            'exercise_minutes': exercise_minutes,
            'water_glasses': water_glasses,
            'meals': meals,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        })
        
        return log_id
    
    @staticmethod
    def get_by_user_id(user_id: int, limit: int = None) -> List[Dict[str, Any]]:
        if user_id not in lifestyle_logs_db:
            return []
        
        logs = sorted(lifestyle_logs_db[user_id], key=lambda x: x['date'], reverse=True)
        if limit and limit > 0:
            return logs[:limit]
        return logs

class Payment:
    @staticmethod
    def create(user_id: int, reference: str, amount: float, currency: str = 'NGN') -> int:
        payment_id = get_next_payment_id()
        
        if user_id not in payments_db:
            payments_db[user_id] = []
        
        payments_db[user_id].append({
            'id': payment_id,
            'user_id': user_id,
            'reference': reference,
            'amount': amount,
            'currency': currency,
            'status': 'pending',
            'gateway_response': {},
            'created_at': datetime.now().isoformat()
        })
        
        return payment_id
    
    @staticmethod
    def update_status(reference: str, status: str, gateway_response: Dict = None):
        for user_payments in payments_db.values():
            for payment in user_payments:
                if payment['reference'] == reference:
                    payment['status'] = status
                    if gateway_response is not None:
                        payment['gateway_response'] = gateway_response
                    return payment
        return None
    
    @staticmethod
    def get_by_reference(reference: str) -> Dict[str, Any] | None:
        for user_payments in payments_db.values():
            for payment in user_payments:
                if payment['reference'] == reference:
                    return payment
        return None
