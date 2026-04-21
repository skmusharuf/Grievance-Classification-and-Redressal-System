"""
Migration Script v2: Add Location Fields and New Tables
Adds location tracking capabilities to existing databases
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/grievance.db'

def migrate_database():
    """Migrate database to v2 with location fields"""
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        print("Run init_db.py first to create a new database")
        return False
    
    print("=" * 50)
    print("DATABASE MIGRATION v2 - Location Features")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Check if location columns already exist
        cursor.execute("PRAGMA table_info(complaints)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'latitude' not in columns:
            print("\n[1/4] Adding location fields to complaints table...")
            
            cursor.execute('ALTER TABLE complaints ADD COLUMN latitude REAL')
            cursor.execute('ALTER TABLE complaints ADD COLUMN longitude REAL')
            cursor.execute('ALTER TABLE complaints ADD COLUMN location_accuracy REAL')
            cursor.execute('ALTER TABLE complaints ADD COLUMN location_address TEXT')
            cursor.execute('ALTER TABLE complaints ADD COLUMN location_timestamp TIMESTAMP')
            
            print("✓ Location fields added to complaints table")
        else:
            print("\n[1/4] Location fields already exist, skipping...")
        
        # Check if audit_logs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'")
        if not cursor.fetchone():
            print("\n[2/4] Creating audit_logs table...")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    action TEXT NOT NULL,
                    target_type TEXT,
                    target_id TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES admins(id)
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_logs_admin ON audit_logs(admin_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at)
            ''')
            
            print("✓ audit_logs table created")
        else:
            print("\n[2/4] audit_logs table already exists, skipping...")
        
        # Check if file_uploads table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_uploads'")
        if not cursor.fetchone():
            print("\n[3/4] Creating file_uploads table...")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    complaint_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    uploaded_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (complaint_id) REFERENCES complaints(id),
                    FOREIGN KEY (uploaded_by) REFERENCES admins(id)
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_files_complaint ON file_uploads(complaint_id)
            ''')
            
            print("✓ file_uploads table created")
        else:
            print("\n[3/4] file_uploads table already exists, skipping...")
        
        # Create backup table for audit logging (if it doesn't exist)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_actions_log'")
        if not cursor.fetchone():
            print("\n[4/4] Creating admin_actions_log table...")
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_actions_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    complaint_id INTEGER,
                    old_value TEXT,
                    new_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES admins(id),
                    FOREIGN KEY (complaint_id) REFERENCES complaints(id)
                )
            ''')
            
            print("✓ admin_actions_log table created")
        else:
            print("\n[4/4] admin_actions_log table already exists, skipping...")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("MIGRATION COMPLETE - v2 features enabled:")
        print("  ✓ Real-time GPS location tracking")
        print("  ✓ Audit logging for security")
        print("  ✓ File upload support")
        print("  ✓ Admin action tracking")
        print("=" * 50)
        
        return True
    
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False

def verify_migration():
    """Verify that migration was successful"""
    
    if not os.path.exists(DB_PATH):
        print("Database not found")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "=" * 50)
    print("MIGRATION VERIFICATION")
    print("=" * 50)
    
    # Check complaints table
    cursor.execute("PRAGMA table_info(complaints)")
    columns = [column[1] for column in cursor.fetchall()]
    
    required_columns = ['latitude', 'longitude', 'location_accuracy', 'location_address', 'location_timestamp']
    missing = [col for col in required_columns if col not in columns]
    
    if missing:
        print(f"\n✗ Complaints table missing columns: {missing}")
        return False
    else:
        print("\n✓ Complaints table has all location fields")
    
    # Check new tables
    required_tables = ['audit_logs', 'file_uploads']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"✗ Missing tables: {missing_tables}")
        return False
    else:
        print("✓ All required tables exist")
    
    # Get database stats
    cursor.execute("SELECT COUNT(*) FROM complaints")
    complaint_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM admins")
    admin_count = cursor.fetchone()[0]
    
    print(f"\nDatabase Statistics:")
    print(f"  - Complaints: {complaint_count}")
    print(f"  - Admins: {admin_count}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("VERIFICATION COMPLETE - All systems ready!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    print(f"\nMigrating database at: {DB_PATH}\n")
    
    if migrate_database():
        verify_migration()
        print("\nYou can now use the new location features!")
    else:
        print("\nPlease fix the errors and try again.")
