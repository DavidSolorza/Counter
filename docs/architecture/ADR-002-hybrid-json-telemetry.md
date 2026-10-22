# ADR-002: Esquema Híbrido Relacional con Payload JSON Flexible

- **Estado:** PROPUESTO
- **Fecha:** 2026-10-22
- **Decisores:** Staff Software Architect & Principal DBA

## 1. Decisión de Diseño

Se adopta un patrón **Hybrid Document-Relational Schema** para la tabla `telemetry_events`. Las columnas de indexación y partición crítica (`site_key`, `event_type`, `page_url`, `created_at`) permanecen relacionales indexadas, mientras que el contenido variable del evento del navegador se delega a una columna flexible `event_data` (`TEXT` en SQLite con validación JSON / `JSONB` en PostgreSQL).

## 2. Diagrama de Flujo del Payload Flexible

```mermaid
sequenceDiagram
    autonumber
    actor SDK as tracker.js
    participant API as Analytics Controller (/api/v1/telemetry)
    participant UC as RecordEventsUseCase
    participant Repo as SqliteEventRepository
    participant DB as SQLite (event_data TEXT)

    SDK->>API: POST { site_key, events: [{ event_type, page_url, event_data: {...} }] }
    API->>UC: execute(site_key, raw_events)
    Note over UC: Normaliza event_data como Dict[str, Any]<br/>Valida invariantes de entidad
    UC->>Repo: save_batch([TelemetryEvent(event_data=dict)])
    Repo->>DB: INSERT INTO telemetry_events (..., event_data) VALUES (..., json.dumps)
    DB-->>Repo: rowcount
    Repo-->>UC: total insertados
    UC-->>API: total
    API-->>SDK: 200 OK { success: true, stored: N }
```

## 3. Consecuencias
- Desacoplamiento total entre las futuras versiones del SDK frontend y las migraciones de base de datos.
- Capacidad de consultar campos JSON nativamente en SQLite mediante funciones `json_extract(event_data, '$.element')`.
