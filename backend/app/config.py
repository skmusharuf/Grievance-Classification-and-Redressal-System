"""
Configuration and constants for the Grievance System
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_PATH = 'data/grievance.db'

# Email configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', EMAIL_USER)

# ML Classification Configuration
CLASSIFICATION_MODEL = "Naive Bayes"  # Trained locally for fast inference

# Constants
VALID_STATUSES = ['Pending', 'In Progress', 'Resolved']
VALID_ROLES = ['super_admin', 'sub_admin', 'department_admin']

DEPARTMENTS = [
    "CM Office (Miscellaneous)",
    "Development Authority",
    "Municipal",
    "Police",
    "Public Works Department",
    "Transport",
    "General"
]

# Cache Configuration (Redis-compatible)
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour default

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # seconds

# Print email configuration on startup
def log_email_config():
    """Log email configuration status"""
    print("\n" + "="*50)
    print("EMAIL CONFIGURATION")
    print("="*50)
    print(f"EMAIL_HOST: {EMAIL_HOST}")
    print(f"EMAIL_PORT: {EMAIL_PORT}")
    print(f"EMAIL_USER: {EMAIL_USER}")
    print(f"EMAIL_PASSWORD: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else '(NOT SET)'}")
    print(f"EMAIL_FROM: {EMAIL_FROM}")
    if EMAIL_USER and EMAIL_PASSWORD:
        print("Email is CONFIGURED - emails will be sent")
    else:
        print("Email is NOT CONFIGURED - OTPs will only print to console")
    print("="*50 + "\n")
