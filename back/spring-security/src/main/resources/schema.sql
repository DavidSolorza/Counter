-- =============================================================================
-- schema.sql (Spring Boot Security Microservice)
-- Base de datos: security.db (SQLite Local)
-- Gobernanza: Límite estricto < 150 líneas.
-- =============================================================================

-- 1. Tabla de Licencias y Clientes B2B
CREATE TABLE IF NOT EXISTS client_licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    site_key TEXT NOT NULL UNIQUE,
    allowed_domain TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_licenses_key ON client_licenses(site_key);

-- 2. Tabla de Usuarios con Soporte Dinámico de Roles (Admin <-> Usuario)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_id TEXT UNIQUE,
    username TEXT NOT NULL,
    email TEXT,
    avatar_url TEXT,
    site_key TEXT REFERENCES client_licenses(site_key) ON DELETE SET NULL,
    role TEXT NOT NULL DEFAULT 'ROLE_CLIENT' CHECK (role IN ('ROLE_ADMIN', 'ROLE_CLIENT', 'ROLE_VIEWER')),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 3. Registros Semilla Iniciales
INSERT OR IGNORE INTO client_licenses (id, client_name, site_key, allowed_domain, is_active)
VALUES (1, 'Cliente Demo Enterprise', 'wk_test_12345', 'localhost,127.0.0.1', 1);

INSERT OR IGNORE INTO users (id, github_id, username, email, avatar_url, site_key, role, is_active)
VALUES (1, '10001', 'admin', 'admin@counter.intelligence', 'https://github.com/ghost.png', 'wk_test_12345', 'ROLE_ADMIN', 1);
