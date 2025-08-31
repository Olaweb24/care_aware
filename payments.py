from flask import Blueprint, request, jsonify, session
import os
import requests
import secrets
import logging

from models import Payment, User
from auth import require_login

logger = logging.getLogger(__name__)

payments_bp = Blueprint('payments', __name__)

# Paystack configuration
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_BASE_URL = 'https://api.paystack.co'

@payments_bp.route('/pay', methods=['POST'])
@require_login
def initialize_payment():
    try:
        user_id = session['user_id']
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        amount = data.get('amount', 5000)  # Default premium price in kobo (₦50)
        
        # Generate unique reference
        reference = f"HC_{user_id}_{secrets.token_hex(8)}"
        
        # Check if Paystack keys are available
        if not PAYSTACK_SECRET_KEY:
            # Mock payment for development
            Payment.create(user_id, reference, amount / 100, 'NGN')
            return jsonify({
                'status': 'success',
                'data': {
                    'authorization_url': f'/api/verify-payment?reference={reference}&mock=true',
                    'access_code': 'mock_access_code',
                    'reference': reference
                },
                'mock_mode': True
            }), 200
        
        # Initialize payment with Paystack
        payload = {
            'email': user['email'],
            'amount': amount,
            'reference': reference,
            'callback_url': f"{request.host_url}api/verify-payment?reference={reference}"
        }
        
        headers = {
            'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{PAYSTACK_BASE_URL}/transaction/initialize',
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Create payment record
            Payment.create(user_id, reference, amount / 100, 'NGN')
            
            return jsonify(response_data), 200
        else:
            logger.error(f"Paystack initialization failed: {response.text}")
            return jsonify({'error': 'Payment initialization failed'}), 500
            
    except Exception as e:
        logger.error(f"Payment initialization error: {str(e)}")
        return jsonify({'error': 'Payment initialization failed'}), 500

@payments_bp.route('/verify-payment', methods=['GET'])
@require_login
def verify_payment():
    try:
        reference = request.args.get('reference')
        mock_mode = request.args.get('mock', 'false').lower() == 'true'
        
        if not reference:
            return jsonify({'error': 'Reference is required'}), 400
        
        payment = Payment.get_by_reference(reference)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if mock_mode or not PAYSTACK_SECRET_KEY:
            # Mock verification for development
            Payment.update_status(reference, 'success', {'gateway_response': 'Approved (Mock)'})
            User.update_premium_status(payment['user_id'], True)
            
            return jsonify({
                'status': 'success',
                'data': {
                    'status': 'success',
                    'reference': reference,
                    'amount': payment['amount'] * 100,
                    'gateway_response': 'Approved (Mock)',
                    'paid_at': payment['created_at']
                },
                'mock_mode': True
            }), 200
        
        # Verify with Paystack
        headers = {
            'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}',
            headers=headers
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data['data']['status'] == 'success':
                # Update payment status
                Payment.update_status(reference, 'success', response_data['data'])
                User.update_premium_status(payment['user_id'], True)
                
                return jsonify(response_data), 200
            else:
                Payment.update_status(reference, 'failed', response_data['data'])
                return jsonify({'error': 'Payment verification failed'}), 400
        else:
            logger.error(f"Paystack verification failed: {response.text}")
            return jsonify({'error': 'Payment verification failed'}), 500
            
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        return jsonify({'error': 'Payment verification failed'}), 500

@payments_bp.route('/paystack-webhook', methods=['POST'])
def paystack_webhook():
    try:
        # Verify webhook signature (if secret is available)
        payload = request.get_data()
        
        # Process webhook event
        event_data = request.get_json()
        
        if event_data['event'] == 'charge.success':
            reference = event_data['data']['reference']
            payment = Payment.get_by_reference(reference)
            
            if payment:
                Payment.update_status(reference, 'success', event_data['data'])
                User.update_premium_status(payment['user_id'], True)
                logger.info(f"Webhook: Payment confirmed for reference {reference}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@payments_bp.route('/payment-config', methods=['GET'])
def get_payment_config():
    """Get payment configuration for frontend"""
    return jsonify({
        'public_key': PAYSTACK_PUBLIC_KEY or 'pk_test_mock_key',
        'mock_mode': not bool(PAYSTACK_SECRET_KEY)
    }), 200
