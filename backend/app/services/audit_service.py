"""Audit logging service for tracking admin actions"""

from datetime import datetime
from app.models.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class AuditLog:
    """Audit logging functionality"""
    
    @staticmethod
    def log_action(admin_id, action, target_type=None, target_id=None, details=None, ip_address=None, user_agent=None):
        """Log an admin action"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_logs 
                (admin_id, action, target_type, target_id, details, ip_address, user_agent, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (admin_id, action, target_type, target_id, details, ip_address, user_agent, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            return False
    
    @staticmethod
    def get_admin_logs(admin_id, limit=100, offset=0):
        """Get audit logs for specific admin"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM audit_logs
                WHERE admin_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (admin_id, limit, offset))
            
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return logs
        except Exception as e:
            logger.error(f"Error retrieving logs: {e}")
            return []
    
    @staticmethod
    def get_action_logs(action, limit=100, offset=0):
        """Get audit logs for specific action"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM audit_logs
                WHERE action = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (action, limit, offset))
            
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return logs
        except Exception as e:
            logger.error(f"Error retrieving action logs: {e}")
            return []
    
    @staticmethod
    def get_complaint_logs(complaint_id, limit=50):
        """Get all logs related to a specific complaint"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM audit_logs
                WHERE target_type = 'complaint' AND target_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (str(complaint_id), limit))
            
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return logs
        except Exception as e:
            logger.error(f"Error retrieving complaint logs: {e}")
            return []
    
    @staticmethod
    def get_logs_by_date_range(start_date, end_date, limit=1000):
        """Get audit logs within date range"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM audit_logs
                WHERE created_at >= ? AND created_at <= ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (start_date, end_date, limit))
            
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return logs
        except Exception as e:
            logger.error(f"Error retrieving date range logs: {e}")
            return []


# Action constants for consistent logging
class AuditActions:
    """Constants for audit log actions"""
    
    # Authentication
    LOGIN_SUCCESS = 'LOGIN_SUCCESS'
    LOGIN_FAILURE = 'LOGIN_FAILURE'
    LOGOUT = 'LOGOUT'
    SESSION_REFRESH = 'SESSION_REFRESH'
    
    # Complaint management
    COMPLAINT_VIEW = 'COMPLAINT_VIEW'
    COMPLAINT_ASSIGNED = 'COMPLAINT_ASSIGNED'
    COMPLAINT_STATUS_CHANGE = 'COMPLAINT_STATUS_CHANGE'
    COMPLAINT_RESOLVED = 'COMPLAINT_RESOLVED'
    COMPLAINT_ESCALATED = 'COMPLAINT_ESCALATED'
    
    # File operations
    FILE_UPLOAD = 'FILE_UPLOAD'
    FILE_DOWNLOAD = 'FILE_DOWNLOAD'
    FILE_DELETE = 'FILE_DELETE'
    
    # Admin operations
    ADMIN_CREATE = 'ADMIN_CREATE'
    ADMIN_UPDATE = 'ADMIN_UPDATE'
    ADMIN_DELETE = 'ADMIN_DELETE'
    ADMIN_ROLE_CHANGE = 'ADMIN_ROLE_CHANGE'
    
    # Security
    FAILED_LOGIN_ATTEMPT = 'FAILED_LOGIN_ATTEMPT'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED'
    SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY'
    
    # Notifications
    EMAIL_SENT = 'EMAIL_SENT'
    NOTIFICATION_SENT = 'NOTIFICATION_SENT'
