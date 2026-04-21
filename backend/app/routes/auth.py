"""Authentication routes with enhanced security"""

from flask import Blueprint, request, jsonify
from app.models.otp import store_auth_otp, verify_auth_otp
from app.models.admin import (
    verify_admin_credentials, create_admin_session, 
    log_failed_login_attempt, is_account_locked, 
    refresh_admin_session, logout_admin_session
)
from app.services.email_service import send_email
from app.utils.validators import validate_admin_login, sanitize_input
from app.config import EMAIL_USER, EMAIL_PASSWORD
import logging

bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger(__name__)

@bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email for verification"""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        otp = store_auth_otp(email)
        
        subject = "Your Grievance System OTP"
        body = f"""
Hello,

Your OTP for the Grievance System is: {otp}

This OTP is valid for 10 minutes.

If you did not request this OTP, please ignore this email.

Thank you,
Grievance System Team
        """
        
        email_sent = send_email(email, subject, body)
        
        print(f"[v0] OTP generated for {email}: {otp}")
        
        response = {
            'success': True,
            'message': 'OTP sent successfully'
        }
        
        if not EMAIL_USER or not EMAIL_PASSWORD:
            response['otp'] = otp
            response['message'] = 'OTP generated (email not configured - check console)'
        
        return jsonify(response)
    
    except Exception as e:
        print(f"[v0] Error sending OTP: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP for email"""
    try:
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        if not all([email, otp]):
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        if not verify_auth_otp(email, otp):
            return jsonify({'error': 'Invalid OTP'}), 401
        
        print(f"[v0] OTP verified successfully for {email}")
        
        return jsonify({
            'success': True,
            'message': 'OTP verified successfully'
        })
    
    except Exception as e:
        print(f"[v0] Error verifying OTP: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login with enhanced security"""
    try:
        data = sanitize_input(request.json)
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate input
        errors = validate_admin_login(email, password)
        if errors:
            logger.warning(f"Login validation failed for {email}: {errors}")
            return jsonify({'error': 'Invalid credentials'}), 400
        
        # Check if account is locked
        if is_account_locked(email):
            logger.warning(f"Login attempt on locked account: {email}")
            return jsonify({
                'error': 'Account temporarily locked due to multiple failed login attempts. Please try again later.'
            }), 429
        
        # Verify credentials
        admin = verify_admin_credentials(email, password)
        if not admin:
            log_failed_login_attempt(email)
            logger.warning(f"Failed login attempt for {email}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create session
        session_token = create_admin_session(admin['id'])
        
        logger.info(f"Admin login successful for {email} (ID: {admin['id']})")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'session_token': session_token,
            'admin': {
                'id': admin['id'],
                'email': admin['email'],
                'name': admin['name'],
                'role': admin['role'],
                'zone_name': admin['zone_name'],
                'circle_name': admin['circle_name']
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error in admin login: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout"""
    try:
        data = request.json
        session_token = data.get('session_token')
        
        if not session_token:
            return jsonify({'error': 'Session token required'}), 400
        
        logout_admin_session(session_token)
        logger.info(f"Admin logged out")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    
    except Exception as e:
        logger.error(f"Error in admin logout: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/admin/refresh-session', methods=['POST'])
def admin_refresh_session():
    """Refresh admin session"""
    try:
        data = request.json
        session_token = data.get('session_token')
        
        if not session_token:
            return jsonify({'error': 'Session token required'}), 400
        
        new_token = refresh_admin_session(session_token)
        if not new_token:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        logger.info("Admin session refreshed")
        
        return jsonify({
            'success': True,
            'message': 'Session refreshed',
            'session_token': new_token
        }), 200
    
    except Exception as e:
        logger.error(f"Error refreshing session: {e}")
        return jsonify({'error': 'Internal server error'}), 500
