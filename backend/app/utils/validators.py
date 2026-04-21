"""Input validation and sanitization utilities"""

import re
import html
from email.utils import parseaddr

def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    
    # RFC 5322 simplified validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:
        return False, "Email too long"
    
    return True, None

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password too long"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def validate_phone(phone):
    """Validate phone number (Indian format)"""
    if not phone:
        return False, "Phone is required"
    
    # Remove non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    
    if len(cleaned) != 10:
        return False, "Phone number must be 10 digits"
    
    return True, None

def validate_aadhar(aadhar):
    """Validate Aadhar number format"""
    if not aadhar:
        return True, None  # Aadhar is optional
    
    # Remove non-digit characters
    cleaned = re.sub(r'\D', '', aadhar)
    
    if len(cleaned) != 12:
        return False, "Aadhar number must be 12 digits"
    
    return True, None

def validate_name(name):
    """Validate name"""
    if not name or not name.strip():
        return False, "Name is required"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name.strip()) > 100:
        return False, "Name too long"
    
    # Allow letters, spaces, and some special characters
    if not re.match(r"^[a-zA-Z\s'-]+$", name):
        return False, "Name contains invalid characters"
    
    return True, None

def validate_description(description):
    """Validate complaint description"""
    if not description or not description.strip():
        return False, "Description is required"
    
    if len(description.strip()) < 10:
        return False, "Description must be at least 10 characters"
    
    if len(description.strip()) > 5000:
        return False, "Description too long"
    
    return True, None

def validate_address(address):
    """Validate address"""
    if not address or not address.strip():
        return False, "Address is required"
    
    if len(address.strip()) < 5:
        return False, "Address must be at least 5 characters"
    
    if len(address.strip()) > 500:
        return False, "Address too long"
    
    return True, None

def validate_location_coordinates(latitude, longitude):
    """Validate GPS coordinates"""
    try:
        lat = float(latitude) if latitude is not None else None
        lon = float(longitude) if longitude is not None else None
        
        if lat is None or lon is None:
            return True, None  # Coordinates are optional
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        
        if not (-180 <= lon <= 180):
            return False, "Longitude must be between -180 and 180"
        
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"

def sanitize_text(text):
    """Sanitize text to prevent XSS"""
    if not text:
        return ""
    
    # HTML escape special characters
    text = html.escape(str(text).strip())
    return text

def sanitize_input(data):
    """Sanitize dictionary of inputs"""
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_text(value)
        else:
            sanitized[key] = value
    
    return sanitized

def validate_complaint_form(data):
    """Validate complete complaint form"""
    errors = {}
    
    # Validate name
    valid, error = validate_name(data.get('name', ''))
    if not valid:
        errors['name'] = error
    
    # Validate email
    valid, error = validate_email(data.get('email', ''))
    if not valid:
        errors['email'] = error
    
    # Validate phone
    valid, error = validate_phone(data.get('phone', ''))
    if not valid:
        errors['phone'] = error
    
    # Validate Aadhar (optional)
    valid, error = validate_aadhar(data.get('aadhar', ''))
    if not valid:
        errors['aadhar'] = error
    
    # Validate description
    valid, error = validate_description(data.get('description', ''))
    if not valid:
        errors['description'] = error
    
    # Validate address
    valid, error = validate_address(data.get('full_address', ''))
    if not valid:
        errors['address'] = error
    
    # Validate category
    if not data.get('category'):
        errors['category'] = "Category is required"
    
    # Validate location if provided
    if data.get('latitude') or data.get('longitude'):
        valid, error = validate_location_coordinates(
            data.get('latitude'),
            data.get('longitude')
        )
        if not valid:
            errors['location'] = error
    
    return errors if errors else None

def validate_admin_login(email, password):
    """Validate admin login credentials"""
    errors = {}
    
    valid, error = validate_email(email)
    if not valid:
        errors['email'] = error
    
    if not password:
        errors['password'] = "Password is required"
    elif len(password) > 128:
        errors['password'] = "Password too long"
    
    return errors if errors else None
