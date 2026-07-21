"""
Multi-city management routes for scalable deployment across India
"""

from flask import Blueprint, request, jsonify
from app.models.database import get_db_connection
from app.middleware.performance import cache_api_response, rate_limit_api

bp = Blueprint('cities', __name__, url_prefix='/api/cities')

# Multi-city seed data for India
INDIA_CITIES_DATA = [
    # Format: (city_code, city_name, state, latitude, longitude)
    ("HYD", "Hyderabad", "Telangana", 17.3850, 78.4867),
    ("BLR", "Bangalore", "Karnataka", 12.9716, 77.5946),
    ("CHN", "Chennai", "Tamil Nadu", 13.0827, 80.2707),
    ("DEL", "Delhi", "Delhi", 28.7041, 77.1025),
    ("MUM", "Mumbai", "Maharashtra", 19.0760, 72.8777),
    ("KOL", "Kolkata", "West Bengal", 22.5726, 88.3639),
    ("PUN", "Pune", "Maharashtra", 18.5204, 73.8567),
    ("JAI", "Jaipur", "Rajasthan", 26.9124, 75.7873),
    ("AHM", "Ahmedabad", "Gujarat", 23.0225, 72.5714),
    ("LKH", "Lucknow", "Uttar Pradesh", 26.8467, 80.9462),
    ("KOC", "Kochi", "Kerala", 9.9312, 76.2673),
    ("AMD", "Surat", "Gujarat", 21.1458, 72.8305),
]

@bp.route('', methods=['GET'])
@cache_api_response(ttl=86400, key_prefix='cities_list')
@rate_limit_api(max_requests=1000, window=3600)
def get_cities():
    """Get all available cities"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, city_code, city_name, state, latitude, longitude, is_active
            FROM cities
            WHERE is_active = 1
            ORDER BY city_name
        ''')
        
        cities = []
        for row in cursor.fetchall():
            cities.append({
                'id': row['id'],
                'city_code': row['city_code'],
                'city_name': row['city_name'],
                'state': row['state'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'is_active': bool(row['is_active'])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'cities': cities,
            'total': len(cities)
        })
    
    except Exception as e:
        print(f"[v0] Error fetching cities: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<city_code>', methods=['GET'])
@cache_api_response(ttl=86400, key_prefix='city_details')
@rate_limit_api(max_requests=1000, window=3600)
def get_city_details(city_code):
    """Get detailed information about a specific city"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, city_code, city_name, state, latitude, longitude, is_active
            FROM cities
            WHERE city_code = ? AND is_active = 1
        ''', (city_code,))
        
        city = cursor.fetchone()
        
        if not city:
            conn.close()
            return jsonify({'error': 'City not found'}), 404
        
        # Get zone statistics
        cursor.execute('''
            SELECT COUNT(*) FROM zones WHERE city_id = ?
        ''', (city['id'],))
        
        zone_count = cursor.fetchone()[0]
        
        # Get total complaints
        cursor.execute('''
            SELECT COUNT(*) FROM complaints WHERE city_id = ?
        ''', (city['id'],))
        
        complaint_count = cursor.fetchone()[0]
        
        # Get complaint breakdown
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM complaints
            WHERE city_id = ?
            GROUP BY status
        ''', (city['id'],))
        
        status_breakdown = {}
        for row in cursor.fetchall():
            status_breakdown[row['status']] = row['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'city': {
                'id': city['id'],
                'city_code': city['city_code'],
                'city_name': city['city_name'],
                'state': city['state'],
                'latitude': city['latitude'],
                'longitude': city['longitude'],
                'zone_count': zone_count,
                'complaint_count': complaint_count,
                'status_breakdown': status_breakdown
            }
        })
    
    except Exception as e:
        print(f"[v0] Error fetching city details: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<city_code>/zones', methods=['GET'])
@cache_api_response(ttl=3600, key_prefix='city_zones')
@rate_limit_api(max_requests=500, window=3600)
def get_city_zones(city_code):
    """Get all zones for a specific city"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get city ID
        cursor.execute('SELECT id FROM cities WHERE city_code = ? AND is_active = 1', (city_code,))
        city = cursor.fetchone()
        
        if not city:
            conn.close()
            return jsonify({'error': 'City not found'}), 404
        
        # Get zones
        cursor.execute('''
            SELECT z.id, z.zone_number, z.zone_name, z.latitude, z.longitude,
                   COUNT(DISTINCT c.id) as circle_count,
                   COUNT(DISTINCT a.id) as area_count,
                   COUNT(DISTINCT comp.id) as complaint_count
            FROM zones z
            LEFT JOIN circles c ON c.zone_id = z.id
            LEFT JOIN areas a ON a.zone_id = z.id
            LEFT JOIN complaints comp ON comp.zone_id = z.id
            WHERE z.city_id = ?
            GROUP BY z.id
            ORDER BY z.zone_number
        ''', (city['id'],))
        
        zones = []
        for row in cursor.fetchall():
            zones.append({
                'id': row['id'],
                'zone_number': row['zone_number'],
                'zone_name': row['zone_name'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'circle_count': row['circle_count'] or 0,
                'area_count': row['area_count'] or 0,
                'complaint_count': row['complaint_count'] or 0
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'city_code': city_code,
            'zones': zones,
            'total': len(zones)
        })
    
    except Exception as e:
        print(f"[v0] Error fetching city zones: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/init-seed', methods=['POST'])
def seed_initial_cities():
    """
    Seed initial cities data (for first-time setup)
    Should be restricted to admin only in production
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if cities already exist
        cursor.execute('SELECT COUNT(*) FROM cities')
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return jsonify({
                'message': 'Cities already seeded',
                'count': count
            })
        
        # Seed cities
        cursor.executemany('''
            INSERT OR IGNORE INTO cities (city_code, city_name, state, latitude, longitude, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', INDIA_CITIES_DATA)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Seeded {len(INDIA_CITIES_DATA)} cities',
            'cities_added': len(INDIA_CITIES_DATA)
        })
    
    except Exception as e:
        print(f"[v0] Error seeding cities: {e}")
        return jsonify({'error': str(e)}), 500
