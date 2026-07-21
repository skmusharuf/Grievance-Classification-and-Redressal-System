"""
Multi-city seed script for production deployment across India
Creates cities, zones, circles, and areas for major Indian cities
"""

import sqlite3
import hashlib
import os
from init_db import DB_PATH

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Major Indian Cities with coordinates
CITIES_DATA = [
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
]

# Generic zones template for all cities (adaptable structure)
ZONES_PER_CITY = 8  # 8 zones per city (can be customized per city)

# Generic circles and areas
CIRCLES_PER_ZONE = 5
AREAS_PER_CIRCLE = 8

def seed_multi_city_database():
    """Seed database with multiple Indian cities"""
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run init_db.py first.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print("\n" + "="*70)
    print("MULTI-CITY PRODUCTION DATABASE SEEDING")
    print("="*70)
    
    # Seed Cities
    print("\n[1/4] Seeding Major Indian Cities...")
    cursor.executemany('''
        INSERT OR IGNORE INTO cities (city_code, city_name, state, latitude, longitude, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', CITIES_DATA)
    conn.commit()
    
    cursor.execute("SELECT id, city_code, city_name FROM cities")
    cities = cursor.fetchall()
    print(f"✓ {len(cities)} cities created")
    
    # Seed Zones, Circles, and Areas for each city
    for city_id, city_code, city_name in cities:
        print(f"\n[2/4] Creating zones for {city_name}...")
        
        zones_data = []
        for zone_num in range(1, ZONES_PER_CITY + 1):
            zone_name = f"Zone {zone_num} ({city_code})"
            # Add some variation to coordinates
            lat = 0  # Will be updated per city
            lon = 0
            zones_data.append((city_id, zone_num, zone_name, lat, lon))
        
        cursor.executemany('''
            INSERT OR IGNORE INTO zones (city_id, zone_number, zone_name, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
        ''', zones_data)
        
        # Get created zones
        cursor.execute('SELECT id, zone_number FROM zones WHERE city_id = ?', (city_id,))
        zones = cursor.fetchall()
        print(f"  ✓ {len(zones)} zones created")
        
        # Seed Circles for each zone
        print(f"[3/4] Creating circles and areas for {city_name}...")
        total_circles = 0
        total_areas = 0
        
        for zone_id, zone_num in zones:
            circles_data = []
            for circle_num in range(1, CIRCLES_PER_ZONE + 1):
                circle_name = f"Circle {circle_num}-Z{zone_num}"
                circles_data.append((zone_id, circle_num, circle_name, 0, 0))
            
            cursor.executemany('''
                INSERT OR IGNORE INTO circles (zone_id, circle_number, circle_name, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
            ''', circles_data)
            
            # Get created circles
            cursor.execute('SELECT id FROM circles WHERE zone_id = ?', (zone_id,))
            circles = cursor.fetchall()
            total_circles += len(circles)
            
            # Seed Areas for each circle
            for circle_id, in circles:
                areas_data = []
                for area_num in range(1, AREAS_PER_CIRCLE + 1):
                    area_name = f"Area {area_num}-C{circle_num}-Z{zone_num}"
                    ward_num = (zone_num - 1) * CIRCLES_PER_ZONE * AREAS_PER_CIRCLE + \
                               (circle_num - 1) * AREAS_PER_CIRCLE + area_num
                    areas_data.append((
                        zone_id, circle_id, area_name, ward_num, 0, 0, 'residential', 50000
                    ))
                
                cursor.executemany('''
                    INSERT OR IGNORE INTO areas 
                    (zone_id, circle_id, area_name, ward_number, latitude, longitude, area_type, population)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', areas_data)
                
                total_areas += len(areas_data)
        
        print(f"  ✓ {total_circles} circles created")
        print(f"  ✓ {total_areas} areas created")
    
    conn.commit()
    
    # Create Super Admin (global)
    print(f"\n[4/4] Creating admin users...")
    
    super_admin = (
        "SA_PROD_001",
        "superadmin@grievancehub-india.com",
        hash_password("SuperAdmin@Prod2025"),
        "Super Administrator - India",
        "9876543210",
        "super_admin",
        None,
        None,
        None
    )
    
    cursor.execute('''
        INSERT OR IGNORE INTO admins 
        (admin_id, email, password_hash, name, phone, role, department, zone_id, circle_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', super_admin)
    
    # Create City Admins (one per city)
    city_admins = []
    for city_id, city_code, city_name in cities:
        city_admins.append((
            f"CA_{city_code}",
            f"admin_{city_code.lower()}@grievancehub-india.com",
            hash_password(f"CityAdmin@{city_code}2025"),
            f"{city_name} Administrator",
            f"98765{city_id:05d}",
            "sub_admin",
            None,
            None,
            None
        ))
    
    cursor.executemany('''
        INSERT OR IGNORE INTO admins 
        (admin_id, email, password_hash, name, phone, role, department, zone_id, circle_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', city_admins)
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("MULTI-CITY DATABASE SEEDING COMPLETE")
    print("="*70)
    print(f"\nCities created: {len(CITIES_DATA)}")
    print(f"Zones per city: {ZONES_PER_CITY}")
    print(f"Circles per zone: {CIRCLES_PER_ZONE}")
    print(f"Areas per circle: {AREAS_PER_CIRCLE}")
    print(f"\nTotal Structure:")
    print(f"  - Cities: {len(CITIES_DATA)}")
    print(f"  - Total Zones: {len(CITIES_DATA) * ZONES_PER_CITY}")
    print(f"  - Total Circles: {len(CITIES_DATA) * ZONES_PER_CITY * CIRCLES_PER_ZONE}")
    print(f"  - Total Areas: {len(CITIES_DATA) * ZONES_PER_CITY * CIRCLES_PER_ZONE * AREAS_PER_CIRCLE}")
    
    print("\n" + "="*70)
    print("DEFAULT LOGIN CREDENTIALS")
    print("="*70)
    print("\nSuper Admin (Global):")
    print("  Email: superadmin@grievancehub-india.com")
    print("  Password: SuperAdmin@Prod2025")
    
    print("\nCity Admins (One per city):")
    for city_id, city_code, city_name in cities:
        print(f"  {city_name}:")
        print(f"    Email: admin_{city_code.lower()}@grievancehub-india.com")
        print(f"    Password: CityAdmin@{city_code}2025")
    
    print("\n" + "="*70)
    print("\nProduction deployment ready!")
    print("="*70 + "\n")

if __name__ == "__main__":
    seed_multi_city_database()
