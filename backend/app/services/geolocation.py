"""
Geolocation service for complaint location-based assignment and analytics
Supports multi-city dynamic location-based routing
"""

from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
from functools import lru_cache

# Nominatim geocoder (free, OpenStreetMap-based)
geocoder = Nominatim(user_agent="grievance-system-prod")

# Cache initialization
location_cache = {}

def get_coordinates_from_address(address):
    """
    Convert address to coordinates using Nominatim
    Returns: (latitude, longitude) or None
    """
    try:
        if not address or len(address.strip()) < 5:
            return None
        
        # Check cache
        if address in location_cache:
            return location_cache[address]
        
        # Rate limit: Nominatim allows ~1 request/second
        time.sleep(0.1)
        
        location = geocoder.geocode(address)
        if location:
            coords = (location.latitude, location.longitude)
            location_cache[address] = coords
            return coords
        
        return None
    except Exception as e:
        print(f"[Geolocation] Error: {e}")
        return None

def get_nearest_circle_and_zone(latitude, longitude, db_connection):
    """
    Find nearest administrative division (circle and zone) using coordinates
    """
    try:
        if not latitude or not longitude:
            return None, None
        
        cursor = db_connection.cursor()
        
        # Get all circles with geolocation
        cursor.execute('''
            SELECT c.id, c.circle_name, c.zone_id, 
                   COALESCE(c.latitude, 0) as lat, 
                   COALESCE(c.longitude, 0) as lon
            FROM circles c
            WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
        ''')
        
        circles = cursor.fetchall()
        
        if not circles:
            return None, None
        
        # Calculate distances and find nearest
        min_distance = float('inf')
        nearest_circle = None
        nearest_zone = None
        
        for circle in circles:
            circle_coords = (circle[3], circle[4])
            user_coords = (latitude, longitude)
            
            try:
                distance = geodesic(user_coords, circle_coords).km
                if distance < min_distance:
                    min_distance = distance
                    nearest_circle = circle[0]
                    nearest_zone = circle[2]
            except Exception as e:
                continue
        
        return nearest_circle, nearest_zone
    
    except Exception as e:
        print(f"[Geolocation] Error finding nearest zone: {e}")
        return None, None

def calculate_resolution_time(created_at, resolved_at):
    """
    Calculate resolution time in hours
    """
    try:
        from datetime import datetime
        
        if isinstance(created_at, str):
            created = datetime.fromisoformat(created_at)
        else:
            created = created_at
        
        if isinstance(resolved_at, str):
            resolved = datetime.fromisoformat(resolved_at)
        else:
            resolved = resolved_at
        
        time_diff = resolved - created
        hours = time_diff.total_seconds() / 3600
        return round(hours, 2)
    except:
        return None

def get_area_statistics(zone_id, circle_id, db_connection):
    """
    Get statistics for a specific area for analytics
    """
    try:
        cursor = db_connection.cursor()
        
        query = '''
            SELECT 
                COUNT(*) as total_complaints,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN criticality = 'Critical' THEN 1 ELSE 0 END) as critical,
                AVG(resolution_time_hours) as avg_resolution_time
            FROM complaints
            WHERE 1=1
        '''
        params = []
        
        if zone_id:
            query += ' AND zone_id = ?'
            params.append(zone_id)
        
        if circle_id:
            query += ' AND circle_id = ?'
            params.append(circle_id)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if result:
            return {
                'total_complaints': result[0] or 0,
                'pending': result[1] or 0,
                'in_progress': result[2] or 0,
                'resolved': result[3] or 0,
                'critical': result[4] or 0,
                'avg_resolution_time_hours': result[5] or 0
            }
        
        return None
    except Exception as e:
        print(f"[Analytics] Error: {e}")
        return None

def get_category_distribution(zone_id=None, circle_id=None, db_connection=None):
    """
    Get complaint distribution by category
    """
    try:
        if not db_connection:
            return {}
        
        cursor = db_connection.cursor()
        
        query = '''
            SELECT category, COUNT(*) as count
            FROM complaints
            WHERE 1=1
        '''
        params = []
        
        if zone_id:
            query += ' AND zone_id = ?'
            params.append(zone_id)
        
        if circle_id:
            query += ' AND circle_id = ?'
            params.append(circle_id)
        
        query += ' GROUP BY category ORDER BY count DESC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        distribution = {}
        for row in results:
            distribution[row[0]] = row[1]
        
        return distribution
    except Exception as e:
        print(f"[Analytics] Error: {e}")
        return {}
