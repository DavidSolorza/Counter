# 🏛️ Arquitectura de Base de Datos Canónica (Producción - PostgreSQL)

> **⚠️ AVISO CRÍTICO DE ARQUITECTURA:**  
> **Esta carpeta contiene la ESTRUCTURA REAL Y CANÓNICA DE LA BASE DE DATOS DE COUNTER.**  
> Los archivos SQLite (`.db`) en las carpetas locales de desarrollo se utilizan **exclusivamente para prototipado rápido sin dependencias externas**. Al desplegar en producción (AWS RDS, Supabase, Neon, Railway o Docker), **estas tablas PostgreSQL son la estructura definitiva y obligatoria** que gobierna todo el ecosistema.

---

## 1. Topología de Datos Multi-Servicio

Counter opera con un desacoplamiento estricto entre **Seguridad/Cuentas** y **Analítica/Eventos**:

```mermaid
erDiagram
    CLIENT_LICENSES ||--o{ USERS : "posee"
    CLIENT_LICENSES ||--o{ AUTH_AUDIT_LOGS : "registra"
    CLIENT_LICENSES ||--o{ TELEMETRY_EVENTS : "valida site_key"
    TELEMETRY_EVENTS ||--o{ SESSION_AGGREGATES : "consolida"
    SESSION_AGGREGATES ||--o{ DAILY_METRICS_ROLLUP : "agrupa diario"

    CLIENT_LICENSES {
        bigserial id PK
        varchar client_name
        varchar site_key UK
        varchar allowed_domain
        int monthly_quota
        smallint is_active
    }
    USERS {
        bigserial id PK
        varchar github_id UK
        varchar username
        varchar email
        varchar site_key FK
        varchar role
    }
    TELEMETRY_EVENTS {
        bigserial id PK
        varchar site_key
        varchar session_id
        varchar event_type
        text page_url
        jsonb event_data
        timestamptz created_at
    }
```

---

## 2. Mapa de Archivos SQL de Producción

| Archivo | Microservicio | Descripción y Claves de Rendimiento |
| :--- | :--- | :--- |
| `01_security_postgres_schema.sql` | Spring Boot (:8080) | Licenciamiento B2B, cuentas de usuario GitHub OAuth, claves públicas/privadas y logs de auditoría. |
| `02_analytics_postgres_schema.sql` | Flask (:5000) | Ingesta masiva con columna `JSONB` e **índice GIN** (`USING gin (event_data)`) para búsqueda sub-milisegundo. |
| `03_seed_production_data.sql` | Bootstrap Global | Licencias iniciales, configuración idempotente con `ON CONFLICT DO NOTHING`. |

---

## 3. ¿Por qué SQLite en Local vs PostgreSQL en Producción?

1. **Local (SQLite):** Cero instalación de software, base de datos en un solo archivo portable (`.db`), ideal para desarrollo frontend/backend ágil y pruebas unitarias inmediatas.
2. **Producción (PostgreSQL):**
   - **Concurrencia ACID Real:** Evita los bloqueos de escritura (`database is locked`) que sufre SQLite bajo cientos de requests concurrentes.
   - **Soporte JSONB + GIN:** Permite indexar internamente las propiedades de telemetría (`element`, `scroll_pct`, etc.) sin penalizar la velocidad.
   - **Escalabilidad Horizontal:** Admite read-replicas, partitioning por fecha y copias de seguridad continuas (WAL archiving).

---

## 4. Guía de Conexión en Producción

### Spring Boot (`application-prod.yml`)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:5432/${DB_NAME:counter_security}
    username: ${DB_USER:postgres}
    password: ${DB_PASSWORD:secret}
  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    hibernate.ddl-auto: validate
```

### Flask Analytics (`config.py` o `.env`)
```bash
DATABASE_URL=postgresql://postgres:secret@db.production:5432/counter_analytics
```
