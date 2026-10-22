-- =============================================================================
-- 001_analytics_schema.sql (Flask Analytics Microservice)
-- Base de datos: analytics.db (SQLite)
-- Gobernanza: Límite estricto < 150 líneas.
-- =============================================================================

CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    page_url TEXT NOT NULL,
    event_data TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_telemetry_site ON telemetry_events(site_key);
CREATE INDEX IF NOT EXISTS idx_telemetry_time ON telemetry_events(created_at);
CREATE INDEX IF NOT EXISTS idx_telemetry_type ON telemetry_events(event_type);
CREATE INDEX IF NOT EXISTS idx_telemetry_url ON telemetry_events(page_url);
