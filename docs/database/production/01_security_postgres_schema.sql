-- =============================================================================
-- ESQUEMA DDL PRODUCCIÓN: 01_security_postgres_schema.sql
-- Microservicio: Spring Boot Security (:8080)
-- Motor de Base de Datos: PostgreSQL 15+ (Enterprise Standard)
-- Nomenclatura: Minúsculas y snake_case estricto
-- Gobernanza: Límite estricto < 150 líneas
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabla Maestra de Licencias y Clientes B2B
CREATE TABLE IF NOT EXISTS client_licenses (
    id BIGSERIAL PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    site_key VARCHAR(120) NOT NULL UNIQUE,
    secret_token VARCHAR(255),
    allowed_domain VARCHAR(500) NOT NULL,
    monthly_quota INTEGER NOT NULL DEFAULT 100000 CHECK (monthly_quota > 0),
    is_active SMALLINT NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    tier VARCHAR(50) NOT NULL DEFAULT 'ENTERPRISE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_licenses_site_key 
    ON client_licenses(site_key);
CREATE INDEX IF NOT EXISTS idx_licenses_active_domain 
    ON client_licenses(site_key, is_active, allowed_domain);

-- 2. Tabla de Usuarios y Cuentas Vinculadas (OAuth GitHub)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    github_id VARCHAR(100) UNIQUE,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(255),
    avatar_url VARCHAR(500),
    site_key VARCHAR(120) REFERENCES client_licenses(site_key) ON DELETE SET NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'ROLE_CLIENT' CHECK (role IN ('ROLE_ADMIN', 'ROLE_CLIENT', 'ROLE_VIEWER')),
    is_active SMALLINT NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_github_id 
    ON users(github_id);
CREATE INDEX IF NOT EXISTS idx_users_site_key 
    ON users(site_key);
CREATE INDEX IF NOT EXISTS idx_users_username 
    ON users(username);

-- 3. Tabla de Auditoría de Autenticación y Acceso
CREATE TABLE IF NOT EXISTS auth_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    site_key VARCHAR(120),
    username VARCHAR(150),
    action VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent VARCHAR(500),
    status VARCHAR(50) NOT NULL CHECK (status IN ('SUCCESS', 'DENIED', 'BLOCKED')),
    details VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_site_created 
    ON auth_audit_logs(site_key, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_status 
    ON auth_audit_logs(status);
