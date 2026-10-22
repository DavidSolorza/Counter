-- =============================================================================
-- database/schemas/001_initial_schema.sql
-- Motor: SQLite 3.x / Compatible con PostgreSQL
-- =============================================================================

CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_key TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    owner_email TEXT NOT NULL DEFAULT 'admin@local.test',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sites_key_active ON sites(site_key, is_active);

CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    page_url TEXT NOT NULL,
    event_data TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_key) REFERENCES sites(site_key) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_telemetry_site_key ON telemetry_events(site_key);
CREATE INDEX IF NOT EXISTS idx_telemetry_created_at ON telemetry_events(created_at);
CREATE INDEX IF NOT EXISTS idx_telemetry_event_type ON telemetry_events(event_type);

INSERT OR IGNORE INTO sites (id, site_key, domain, owner_email, is_active)
VALUES (1, 'wk_test_12345', 'localhost', 'dev@wolfstats.local', 1);
