"""
Grievance System - Production-Grade Flask Application
Multi-city, scalable, with ML-based classification and advanced features
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from python_json_logger import jsonlogger

def create_app():
    """Create and configure the production-grade Flask app"""
    app = Flask(__name__)
    
    # CORS Configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "max_age": 86400
        }
    })
    
    # Rate Limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # JSON Logging
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    app.logger.addHandler(logHandler)
    app.logger.setLevel(logging.INFO)
    
    # Error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': str(e.description)
        }), 429
    
    @app.errorhandler(404)
    def not_found_handler(e):
        return jsonify({
            'error': 'Not found',
            'message': 'Endpoint does not exist'
        }), 404
    
    @app.errorhandler(500)
    def internal_error_handler(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Please try again later'
        }), 500
    
    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    # Register blueprints
    from app.routes import auth, zones, complaints, admin, categories, cities
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(zones.bp)
    app.register_blueprint(complaints.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(cities.bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'version': '2.1.0',
            'features': [
                'Multi-city support',
                'ML-based classification',
                'Geolocation support',
                'Response caching',
                'Rate limiting',
                'Advanced analytics'
            ]
        })
    
    return app
