-- =============================================================================
-- schema.sql (Spring Boot Security Microservice)
-- Base de datos: security.db (SQLite)
-- Gobernanza: Límite estricto < 150 líneas.
-- =============================================================================

CREATE TABLE IF NOT EXISTS client_licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    site_key TEXT NOT NULL UNIQUE,
    allowed_domain TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_licenses_key ON client_licenses(site_key);

-- Registro semilla de prueba
INSERT OR IGNORE INTO client_licenses (id, client_name, site_key, allowed_domain, is_active)
VALUES (1, 'Cliente Demo Enterprise', 'wk_test_12345', 'localhost,127.0.0.1', 1);
