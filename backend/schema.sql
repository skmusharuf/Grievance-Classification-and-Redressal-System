-- SQLite/PostgreSQL-compatible logical schema for the first production migration.
CREATE TABLE IF NOT EXISTS wards (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL, boundary_geojson TEXT, admin_scope TEXT NOT NULL DEFAULT 'ward');
CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, sla_hours INTEGER NOT NULL DEFAULT 72);
CREATE TABLE IF NOT EXISTS complaints (id TEXT PRIMARY KEY, tracking_code_hash TEXT NOT NULL UNIQUE, description TEXT NOT NULL, language TEXT NOT NULL, contact_ciphertext TEXT, address_ciphertext TEXT, latitude_rounded REAL, longitude_rounded REAL, ward_id INTEGER REFERENCES wards(id), department_id INTEGER REFERENCES departments(id), category TEXT, severity TEXT, classifier_version TEXT, classifier_confidence REAL, status TEXT NOT NULL DEFAULT 'registered', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS complaint_events (id INTEGER PRIMARY KEY, complaint_id TEXT NOT NULL REFERENCES complaints(id), actor_id TEXT, event_type TEXT NOT NULL, from_status TEXT, to_status TEXT, note TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS admin_scopes (admin_id TEXT NOT NULL, ward_id INTEGER REFERENCES wards(id), department_id INTEGER REFERENCES departments(id), PRIMARY KEY (admin_id, ward_id, department_id));
CREATE INDEX IF NOT EXISTS complaints_ward_status_idx ON complaints(ward_id, status);
CREATE INDEX IF NOT EXISTS complaint_events_complaint_idx ON complaint_events(complaint_id, created_at);
