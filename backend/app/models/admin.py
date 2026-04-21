"""Admin model - database operations for admins"""

import bcrypt
import uuid
from datetime import datetime, timedelta
from app.models.database import get_db_connection

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def verify_admin_credentials(email, password):
    """Verify admin email and password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.*, z.zone_name, c.circle_name
        FROM admins a
        LEFT JOIN zones z ON z.id = a.zone_id
        LEFT JOIN circles c ON c.id = a.circle_id
        WHERE a.email = ? AND a.is_active = 1
    ''', (email,))
    
    admin = cursor.fetchone()
    conn.close()
    
    if not admin:
        return None
    
    # Verify password using bcrypt
    if not verify_password(password, admin['password_hash']):
        return None
    
    return admin

def create_admin_session(admin_id):
    """Create a new admin session"""
    session_token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=24)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO admin_sessions (session_token, admin_id, expires_at)
        VALUES (?, ?, ?)
    ''', (session_token, admin_id, expires_at.isoformat()))
    
    conn.commit()
    conn.close()
    
    return session_token

def verify_admin_session(session_token):
    """Verify admin session and return admin info"""
    if not session_token:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.*, z.zone_name, c.circle_name, s.expires_at
        FROM admin_sessions s
        JOIN admins a ON a.id = s.admin_id
        LEFT JOIN zones z ON z.id = a.zone_id
        LEFT JOIN circles c ON c.id = a.circle_id
        WHERE s.session_token = ? AND s.is_active = 1
    ''', (session_token,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    # Check expiration
    if result['expires_at']:
        expires = datetime.fromisoformat(result['expires_at'])
        if datetime.now() > expires:
            return None
    
    return dict(result)

def logout_admin_session(session_token):
    """Invalidate admin session"""
    if session_token:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE admin_sessions SET is_active = 0 WHERE session_token = ?
        ''', (session_token,))
        
        conn.commit()
        conn.close()

def refresh_admin_session(session_token):
    """Refresh admin session expiration"""
    if not session_token:
        return None
    
    # Get current session
    admin = verify_admin_session(session_token)
    if not admin:
        return None
    
    # Create new session
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Invalidate old session
    cursor.execute('UPDATE admin_sessions SET is_active = 0 WHERE session_token = ?', (session_token,))
    
    # Create new session
    new_token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=24)
    
    cursor.execute('''
        INSERT INTO admin_sessions (session_token, admin_id, expires_at)
        VALUES (?, ?, ?)
    ''', (new_token, admin['id'], expires_at.isoformat()))
    
    conn.commit()
    conn.close()
    
    return new_token

def log_failed_login_attempt(email):
    """Log failed login attempt for rate limiting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create audit log (will implement with audit service later)
    cursor.execute('''
        INSERT INTO audit_logs (action, target_type, target_id, details)
        VALUES ('FAILED_LOGIN', 'admin', ?, ?)
    ''', (email, f"Failed login attempt for {email}"))
    
    conn.commit()
    conn.close()

def get_failed_login_attempts(email, minutes=15):
    """Get number of failed login attempts in last N minutes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    from datetime import timedelta
    cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
    
    cursor.execute('''
        SELECT COUNT(*) as count FROM audit_logs
        WHERE action = 'FAILED_LOGIN' 
        AND target_id = ? 
        AND created_at > ?
    ''', (email, cutoff_time))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['count'] if result else 0

def is_account_locked(email, max_attempts=5, lockout_minutes=15):
    """Check if admin account is locked due to failed attempts"""
    attempts = get_failed_login_attempts(email, lockout_minutes)
    return attempts >= max_attempts
