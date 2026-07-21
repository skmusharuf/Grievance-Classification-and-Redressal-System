"""
Performance middleware: caching, rate limiting, and response optimization
"""

import time
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps
from app.config import CACHE_ENABLED, CACHE_TTL, RATE_LIMIT_ENABLED, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

# In-memory cache (can be replaced with Redis for multi-instance deployment)
cache_store = {}
rate_limit_store = {}

class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    @staticmethod
    def set(key, value, ttl=CACHE_TTL):
        """Set cache value with expiration"""
        if not CACHE_ENABLED:
            return
        
        cache_store[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }
    
    @staticmethod
    def get(key):
        """Get cache value if not expired"""
        if not CACHE_ENABLED or key not in cache_store:
            return None
        
        entry = cache_store[key]
        
        # Check expiration
        if datetime.now() > entry['expires_at']:
            del cache_store[key]
            return None
        
        return entry['value']
    
    @staticmethod
    def delete(key):
        """Delete cache entry"""
        if key in cache_store:
            del cache_store[key]
    
    @staticmethod
    def clear():
        """Clear all cache"""
        global cache_store
        cache_store = {}

class RateLimiter:
    """Rate limiter using token bucket algorithm"""
    
    @staticmethod
    def is_allowed(identifier, requests=RATE_LIMIT_REQUESTS, window=RATE_LIMIT_WINDOW):
        """Check if request is within rate limit"""
        if not RATE_LIMIT_ENABLED:
            return True
        
        now = datetime.now()
        
        if identifier not in rate_limit_store:
            rate_limit_store[identifier] = []
        
        # Remove old requests outside the window
        rate_limit_store[identifier] = [
            req_time for req_time in rate_limit_store[identifier]
            if (now - req_time).total_seconds() < window
        ]
        
        # Check limit
        if len(rate_limit_store[identifier]) >= requests:
            return False
        
        # Add current request
        rate_limit_store[identifier].append(now)
        return True

def cache_api_response(ttl=CACHE_TTL, key_prefix=''):
    """Decorator for caching API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not CACHE_ENABLED:
                return f(*args, **kwargs)
            
            # Generate cache key
            from flask import request
            cache_key = f"{key_prefix}:{request.path}:{request.query_string.decode()}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Check cache
            cached_response = CacheManager.get(cache_key)
            if cached_response:
                print(f"[Cache] HIT: {cache_key}")
                return cached_response
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Store in cache
            CacheManager.set(cache_key, result, ttl)
            print(f"[Cache] SET: {cache_key} (TTL: {ttl}s)")
            
            return result
        
        return decorated_function
    
    return decorator

def rate_limit_api(max_requests=RATE_LIMIT_REQUESTS, window=RATE_LIMIT_WINDOW):
    """Decorator for rate limiting API endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not RATE_LIMIT_ENABLED:
                return f(*args, **kwargs)
            
            from flask import request, jsonify
            
            # Get client identifier (IP or user ID)
            identifier = request.remote_addr
            if 'user_id' in kwargs:
                identifier = f"user:{kwargs['user_id']}"
            
            if not RateLimiter.is_allowed(identifier, max_requests, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'max_requests': max_requests,
                    'window_seconds': window
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def compress_response(f):
    """Decorator for compressing large responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, make_response
        import gzip
        import io
        
        result = f(*args, **kwargs)
        
        # Check if gzip is supported by client
        if 'gzip' not in request.headers.get('Accept-Encoding', ''):
            return result
        
        # Skip non-JSON responses
        if not isinstance(result, (dict, list)):
            return result
        
        # Serialize to JSON
        json_str = json.dumps(result)
        
        # Only compress if large enough
        if len(json_str) < 1000:
            return result
        
        # Compress
        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gz:
            gz.write(json_str.encode('utf-8'))
        
        gzip_data = gzip_buffer.getvalue()
        
        response = make_response(gzip_data)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = len(gzip_data)
        
        return response
    
    return decorated_function

def log_performance(f):
    """Decorator for logging endpoint performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = (time.time() - start_time) * 1000  # Convert to ms
        
        print(f"[Performance] {request.method} {request.path} - {duration:.2f}ms")
        
        return result
    
    return decorated_function
