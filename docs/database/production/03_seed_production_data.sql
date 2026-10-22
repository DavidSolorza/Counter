-- =============================================================================
-- DATOS SEMILLA PRODUCCIÓN: 03_seed_production_data.sql
-- Inserción idempotente de licencias maestras y usuarios de arranque
-- Gobernanza: Límite estricto < 150 líneas
-- =============================================================================

-- 1. Licencia de Producción por Defecto (Demo / Prototipado Seguro)
INSERT INTO client_licenses (client_name, site_key, secret_token, allowed_domain, monthly_quota, is_active, tier)
VALUES 
    ('Enterprise Demo Client', 'wk_live_demo', 'cntr_sec_prod_live_demo_9823412', 'localhost,127.0.0.1,counter.intelligence', 500000, 1, 'ENTERPRISE'),
    ('QA Test Environment', 'wk_test_12345', 'cntr_sec_prod_test_env_1122334', 'localhost,127.0.0.1', 100000, 1, 'DEVELOPER')
ON CONFLICT (site_key) DO NOTHING;

-- 2. Usuario Administrador Inicial
INSERT INTO users (github_id, username, email, avatar_url, site_key, role, is_active)
VALUES 
    ('10001', 'admin', 'admin@counter.intelligence', 'https://github.com/ghost.png', 'wk_live_demo', 'ROLE_ADMIN', 1)
ON CONFLICT (github_id) DO NOTHING;

-- 3. Registro Inicial de Auditoría
INSERT INTO auth_audit_logs (site_key, username, action, ip_address, status, details)
VALUES 
    ('wk_live_demo', 'system_init', 'DATABASE_INITIALIZATION', '127.0.0.1', 'SUCCESS', 'Production schema mounted and seeded successfully');
