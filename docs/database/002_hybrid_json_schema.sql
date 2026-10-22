-- =============================================================================
-- Archivo DDL: 002_hybrid_json_schema.sql
-- Descripción: Migración a esquema híbrido con columna JSON flexible para SQLite.
-- Nomenclatura: Minúsculas y snake_case estricto
-- =============================================================================

-- 1. Asegurar la creación o migración de la tabla telemetry_events
CREATE TABLE IF NOT EXISTS telemetry_events_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    page_url TEXT NOT NULL,
    event_data TEXT DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_key) REFERENCES sites(site_key) ON DELETE CASCADE
);

-- 2. Migrar datos existentes si la tabla anterior existe
INSERT INTO telemetry_events_new (id, site_key, event_type, page_url, event_data, created_at)
SELECT 
    id, 
    site_key, 
    event_type, 
    page_url, 
    json_object('element', COALESCE(element_target, '')), 
    created_at
FROM telemetry_events
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='telemetry_events');

-- 3. Reemplazo atómico de tabla
DROP TABLE IF EXISTS telemetry_events;
ALTER TABLE telemetry_events_new RENAME TO telemetry_events;

-- 4. Recrear índices optimizados
CREATE INDEX IF NOT EXISTS idx_telemetry_site_key ON telemetry_events(site_key);
CREATE INDEX IF NOT EXISTS idx_telemetry_created_at ON telemetry_events(created_at);
CREATE INDEX IF NOT EXISTS idx_telemetry_event_type ON telemetry_events(event_type);
