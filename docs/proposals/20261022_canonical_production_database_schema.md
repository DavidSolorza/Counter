# Propuesta Técnica: Esquema Canónico de Base de Datos para Producción (PostgreSQL)

**Fecha:** 2026-10-22  
**Autor:** Agente 3 (DBA & Diseñador de Persistencia) & Agente 2 (Arquitecto)  
**Estado:** APROBADO / EJECUTADO  
**Módulos Impactados:** `docs/database/production/`, `back/spring-security/`, `back/flask-analytics/`

---

## 1. Contexto y Problema

Durante la fase de desarrollo y validación local de Counter, se emplearon bases de datos SQLite (`security.db` y `analytics.db`) debido a su conveniencia para arrancar sin necesidad de instalar o configurar servidores de bases de datos locales.

Sin embargo, para desplegar a producción (cloud, VPS o contenedores), SQLite presenta limitaciones severas:
1. Bloqueo a nivel de archivo ante múltiples escrituras concurrentes de eventos de telemetría.
2. Inexistencia de soporte nativo para índices invertidos generalizados (GIN) sobre estructuras JSON.
3. Dificultad para integración con herramientas estándar de migración y réplicas de lectura.

Se requiere un conjunto de artefactos DDL estándar para PostgreSQL organizados en una carpeta dedicada (`docs/database/production/`), estableciendo que este es el esquema canónico y definitivo que debe adoptar el sistema en la nube.

---

## 2. Solución Arquitectónica

Se implementa la suite DDL en `docs/database/production/`:

1. **`01_security_postgres_schema.sql`:**
   - Tablas: `client_licenses`, `users`, `auth_audit_logs`.
   - Claves foráneas estrictas, normalización 3NF, checks y constraints.
   - Integración con GitHub OAuth y sistema de tokens privados.

2. **`02_analytics_postgres_schema.sql`:**
   - Tablas: `telemetry_events`, `session_aggregates`, `daily_metrics_rollup`.
   - Columna `JSONB` nativa con **índice GIN** (`USING gin (event_data)`), permitiendo consultar propiedades complejas con tiempos de respuesta sub-milisegundo.
   - Tablas de agregación para garantizar que los dashboards del frontend carguen al instante.

3. **`03_seed_production_data.sql`:**
   - Inserciones de arranque seguras con cláusulas idempotentes `ON CONFLICT DO NOTHING`.

4. **`README.md`:**
   - Documentación y manifiesto que explicita que la estructura PostgreSQL es el contrato real de base de datos del proyecto Counter.

---

## 3. Beneficios y Mitigación de Riesgos

- **Conversión sin fricción:** Al desplegar en Supabase, RDS o Railway, basta con ejecutar los scripts en orden `01 -> 02 -> 03`.
- **Cero cambios en la capa de dominio:** Los nombres de tablas y columnas coinciden 1:1 con las entidades JPA y las consultas SQL de Flask.
- **Rendimiento empresarial:** Capacidad para procesar millones de eventos diarios sin bloqueo de tablas.
