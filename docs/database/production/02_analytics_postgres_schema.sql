-- =============================================================================
-- ESQUEMA DDL PRODUCCIÓN: 02_analytics_postgres_schema.sql
-- Microservicio: Flask Analytics Engine (:5000)
-- Motor de Base de Datos: PostgreSQL 15+ (Enterprise Standard)
-- Optimización: JSONB nativo con índices GIN para sub-milisegundo
-- Gobernanza: Límite estricto < 150 líneas
-- =============================================================================

-- 1. Tabla de Eventos de Telemetría (Ingesta Masiva de Eventos)
CREATE TABLE IF NOT EXISTS telemetry_events (
    id BIGSERIAL PRIMARY KEY,
    site_key VARCHAR(120) NOT NULL,
    session_id VARCHAR(120),
    event_type VARCHAR(64) NOT NULL,
    page_url VARCHAR(1024) NOT NULL,
    element_selector VARCHAR(255),
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    client_ip VARCHAR(45),
    user_agent VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices B-Tree para filtrado rápido por cliente y ventana temporal
CREATE INDEX IF NOT EXISTS idx_telemetry_site_time 
    ON telemetry_events(site_key, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_site_type 
    ON telemetry_events(site_key, event_type);
CREATE INDEX IF NOT EXISTS idx_telemetry_session 
    ON telemetry_events(session_id);

-- Índice GIN para búsquedas instantáneas sobre atributos JSONB (element, scroll, etc.)
CREATE INDEX IF NOT EXISTS idx_telemetry_event_data_gin 
    ON telemetry_events USING gin (event_data);

-- 2. Tabla de Agregados de Sesión (Pre-cálculo para dashboards)
CREATE TABLE IF NOT EXISTS session_aggregates (
    id BIGSERIAL PRIMARY KEY,
    site_key VARCHAR(120) NOT NULL,
    session_id VARCHAR(120) NOT NULL,
    total_events INTEGER NOT NULL DEFAULT 0,
    pageviews_count INTEGER NOT NULL DEFAULT 0,
    clicks_count INTEGER NOT NULL DEFAULT 0,
    rage_clicks_count INTEGER NOT NULL DEFAULT 0,
    dead_clicks_count INTEGER NOT NULL DEFAULT 0,
    friction_score NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_site_session UNIQUE (site_key, session_id)
);

CREATE INDEX IF NOT EXISTS idx_session_agg_site_friction 
    ON session_aggregates(site_key, friction_score DESC);
CREATE INDEX IF NOT EXISTS idx_session_agg_started 
    ON session_aggregates(site_key, started_at DESC);

-- 3. Tabla de Métricas Consolidadas Diarias (Rollups para analítica histórica)
CREATE TABLE IF NOT EXISTS daily_metrics_rollup (
    id BIGSERIAL PRIMARY KEY,
    site_key VARCHAR(120) NOT NULL,
    metric_date DATE NOT NULL,
    total_events INTEGER NOT NULL DEFAULT 0,
    unique_sessions INTEGER NOT NULL DEFAULT 0,
    avg_friction_score NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    rage_click_events INTEGER NOT NULL DEFAULT 0,
    top_friction_url VARCHAR(1024),
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_site_date UNIQUE (site_key, metric_date)
);

CREATE INDEX IF NOT EXISTS idx_rollup_site_date 
    ON daily_metrics_rollup(site_key, metric_date DESC);
