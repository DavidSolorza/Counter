-- =============================================================================
-- Archivo DDL: 001_initial_schema.sql
-- Descripción: Esquema inicial para sitios (licencias) y eventos de telemetría.
-- Motor: SQLite 3.x
-- Nomenclatura: Minúsculas y snake_case estricto
-- =============================================================================

-- 1. Tabla de Sitios / Licencias
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_key TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL,
    owner_email TEXT NOT NULL DEFAULT 'admin@local.test',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sites_site_key_active 
ON sites(site_key, is_active);

-- 2. Tabla de Eventos de Telemetría
CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    element_target TEXT,
    page_url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_key) REFERENCES sites(site_key) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_telemetry_site_key 
ON telemetry_events(site_key);

CREATE INDEX IF NOT EXISTS idx_telemetry_created_at 
ON telemetry_events(created_at);

-- 3. Inserción de Semilla (Seed) de Prueba
INSERT OR IGNORE INTO sites (id, site_key, domain, owner_email, is_active)
VALUES (1, 'wk_test_12345', 'localhost', 'dev@wolfstats.local', 1);
