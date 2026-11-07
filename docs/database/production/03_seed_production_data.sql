-- =============================================================================
-- DATOS SEMILLA PRODUCCIÓN: 03_seed_production_data.sql
-- Inserción idempotente de licencias maestras y usuarios de arranque
-- Gobernanza: Límite estricto < 150 líneas
-- =============================================================================

-- 1. Licencias Maestras de Producción y Proyectos Registrados
INSERT INTO client_licenses (client_name, site_key, secret_token, allowed_domain, monthly_quota, is_active, tier)
VALUES 
    ('Enterprise Demo Client', 'wk_live_demo', 'cntr_sec_prod_live_demo_9823412', '*,localhost,127.0.0.1,*.servidor.blog,*.vercel.app', 500000, 1, 'ENTERPRISE'),
    ('QA Test Environment', 'wk_test_12345', 'cntr_sec_prod_test_env_1122334', '*,localhost,127.0.0.1,*.servidor.blog,*.vercel.app', 100000, 1, 'DEVELOPER'),
    ('David Solorza', 'cntr_davidsolorza_chsfoi2w2iib63p1jla3vuql', 'cntr_sec_david_unified_7788990', '*,localhost,127.0.0.1,*.servidor.blog,*.vercel.app', 500000, 1, 'ENTERPRISE'),
    ('David Solorza (Google OAuth)', 'cntr_google_davidsolorza_5e5155tr04j2nk12vy6v7nqp', 'cntr_sec_david_google_5544332', '*,localhost,127.0.0.1,*.servidor.blog,*.vercel.app', 500000, 1, 'ENTERPRISE'),
    ('Streaming Colombia', 'cntr_streaming_live_prod', 'cntr_sec_streaming_prod_3391821', '*,localhost,127.0.0.1,streaming-brown-rho.vercel.app,*.vercel.app,*.servidor.blog', 500000, 1, 'ENTERPRISE'),
    ('AgroMap', 'cntr_agromap_live_prod', 'cntr_sec_agromap_prod_8841209', '*,localhost,127.0.0.1,agromap-phi.vercel.app,*.vercel.app,*.servidor.blog', 250000, 1, 'ENTERPRISE'),
    ('Plantas Lecheras', 'cntr_plantaslecheras_live_prod', 'cntr_sec_plantas_prod_4491023', '*,localhost,127.0.0.1,plantas-lecheras.vercel.app,*.vercel.app,*.servidor.blog', 250000, 1, 'ENTERPRISE'),
    ('Portal de Clientes', 'cntr_clientportal_live_prod', 'cntr_sec_portal_prod_9918273', '*,localhost,127.0.0.1,portal-clientes-kappa.vercel.app,*.vercel.app,*.servidor.blog', 250000, 1, 'ENTERPRISE'),
    ('Agenda Nuestros Planes', 'cntr_agenda_live_prod', 'cntr_sec_agenda_prod_1182736', '*,localhost,127.0.0.1,*.vercel.app,*.servidor.blog', 250000, 1, 'ENTERPRISE')
ON CONFLICT (site_key) DO UPDATE SET
    allowed_domain = EXCLUDED.allowed_domain,
    secret_token = COALESCE(client_licenses.secret_token, EXCLUDED.secret_token),
    updated_at = CURRENT_TIMESTAMP;

-- 2. Usuario Administrador Inicial
INSERT INTO users (github_id, username, email, avatar_url, site_key, role, is_active)
VALUES 
    ('10001', 'admin', 'admin@counter.intelligence', 'https://github.com/ghost.png', 'wk_live_demo', 'ROLE_ADMIN', 1)
ON CONFLICT (github_id) DO NOTHING;

-- 3. Registro Inicial de Auditoría
INSERT INTO auth_audit_logs (site_key, username, action, ip_address, status, details)
VALUES 
    ('wk_live_demo', 'system_init', 'DATABASE_INITIALIZATION', '127.0.0.1', 'SUCCESS', 'Production schema mounted and seeded successfully');
