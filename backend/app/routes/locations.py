"""Location-related API endpoints for complaint tracking"""

from flask import Blueprint, request, jsonify
from app.models.complaint import get_complaints_with_locations, update_complaint_location
from app.models.admin import verify_admin_session
from app.utils.validators import validate_location_coordinates
from app.services.audit_service import AuditLog, AuditActions
import logging

bp = Blueprint('locations', __name__, url_prefix='/api/locations')
logger = logging.getLogger(__name__)

@bp.route('/submit-with-location', methods=['POST'])
def submit_complaint_with_location():
    """Submit a complaint with location data"""
    try:
        data = request.json
        
        # Validate location data
        valid, error = validate_location_coordinates(data.get('latitude'), data.get('longitude'))
        if not valid:
            return jsonify({'error': error}), 400
        
        # This is called from the complaint route, so we just return success
        # The complaint route handles the actual submission
        return jsonify({
            'success': True,
            'message': 'Location data validated',
            'location': {
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'accuracy': data.get('location_accuracy'),
                'address': data.get('location_address')
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error in location submission: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/map-data', methods=['GET'])
def get_map_data():
    """Get all complaint locations for admin map view"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Verify admin session
        admin = verify_admin_session(session_token)
        if not admin:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Get filter parameters
        zone_id = request.args.get('zone_id')
        circle_id = request.args.get('circle_id')
        status = request.args.get('status')
        
        # Get complaints with location data
        complaints = get_complaints_with_locations(zone_id, circle_id, status)
        
        # Log the action
        AuditLog.log_action(
            admin['id'],
            AuditActions.COMPLAINT_VIEW,
            target_type='map',
            details=f"Viewed complaint map. Zone: {zone_id}, Circle: {circle_id}, Status: {status}"
        )
        
        # Convert to map-friendly format
        locations = []
        for complaint in complaints:
            locations.append({
                'id': complaint['complaint_id'],
                'db_id': complaint['id'],
                'name': complaint['name'],
                'email': complaint['email'],
                'phone': complaint['phone'],
                'description': complaint['description'][:100] + '...' if len(complaint['description']) > 100 else complaint['description'],
                'category': complaint['category'],
                'criticality': complaint['criticality'],
                'status': complaint['status'],
                'latitude': complaint['latitude'],
                'longitude': complaint['longitude'],
                'accuracy': complaint['location_accuracy'],
                'address': complaint['location_address'],
                'zone_name': complaint['zone_name'],
                'circle_name': complaint['circle_name'],
                'created_at': complaint['created_at']
            })
        
        logger.info(f"Admin {admin['email']} viewed map data with {len(locations)} locations")
        
        return jsonify({
            'success': True,
            'count': len(locations),
            'locations': locations
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting map data: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/<complaint_id>/update-location', methods=['PUT'])
def update_location(complaint_id):
    """Update location for a specific complaint"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Verify admin session
        admin = verify_admin_session(session_token)
        if not admin:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        data = request.json
        
        # Validate location data
        valid, error = validate_location_coordinates(data.get('latitude'), data.get('longitude'))
        if not valid:
            return jsonify({'error': error}), 400
        
        # Update location
        update_complaint_location(
            complaint_id,
            data.get('latitude'),
            data.get('longitude'),
            data.get('location_accuracy'),
            data.get('location_address')
        )
        
        # Log the action
        AuditLog.log_action(
            admin['id'],
            AuditActions.COMPLAINT_VIEW,
            target_type='complaint',
            target_id=complaint_id,
            details=f"Updated location for complaint {complaint_id}"
        )
        
        logger.info(f"Admin {admin['email']} updated location for complaint {complaint_id}")
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'location': {
                'complaint_id': complaint_id,
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'accuracy': data.get('location_accuracy'),
                'address': data.get('location_address')
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/nearby', methods=['GET'])
def get_nearby_complaints():
    """Get complaints near a specific location"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_token:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Verify admin session
        admin = verify_admin_session(session_token)
        if not admin:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Get parameters
        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('lon'))
        radius_km = float(request.args.get('radius', 5))  # Default 5km radius
        
        # Validate coordinates
        valid, error = validate_location_coordinates(latitude, longitude)
        if not valid:
            return jsonify({'error': error}), 400
        
        # Get all complaints with locations
        all_complaints = get_complaints_with_locations()
        
        # Calculate distances and filter by radius
        import math
        nearby = []
        
        for complaint in all_complaints:
            # Haversine formula for distance calculation
            lat1, lon1 = math.radians(latitude), math.radians(longitude)
            lat2, lon2 = math.radians(float(complaint['latitude'])), math.radians(float(complaint['longitude']))
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth's radius in km
            distance_km = 6371 * c
            
            if distance_km <= radius_km:
                nearby.append({
                    **{k: v for k, v in dict(complaint).items() if k in [
                        'complaint_id', 'name', 'email', 'phone', 'category',
                        'status', 'latitude', 'longitude', 'created_at'
                    ]},
                    'distance_km': round(distance_km, 2)
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        
        logger.info(f"Admin {admin['email']} queried nearby complaints at ({latitude}, {longitude}) within {radius_km}km - found {len(nearby)}")
        
        return jsonify({
            'success': True,
            'count': len(nearby),
            'center': {'latitude': latitude, 'longitude': longitude},
            'radius_km': radius_km,
            'complaints': nearby
        }), 200
    
    except ValueError:
        return jsonify({'error': 'Invalid latitude, longitude, or radius'}), 400
    except Exception as e:
        logger.error(f"Error getting nearby complaints: {e}")
        return jsonify({'error': 'Internal server error'}), 500
