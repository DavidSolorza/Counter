# ADR-003: Arquitectura Tripartita Desacoplada y SDK Empresarial

- **Estado:** PROPUESTO
- **Fecha:** 2026-10-22
- **Decisores:** Staff Software Architect & VP of Engineering

## 1. Decisión de Diseño

Se reestructura el proyecto en tres componentes con responsabilidades estrictamente separadas:
1. `sdk/`: Entorno independiente para el cliente de telemetría.
2. `backend/`: Capa de servicios REST, enriquecimiento (User-Agent, IP) y procesamiento en memoria.
3. `database/`: Capa de persistencia, DDL y adaptadores de repositorios.

Toda la comunicación fluye a través de una API REST unificada con endpoints desacoplados:
- `POST /api/v1/verify` (Handshake)
- `POST /api/v1/telemetry` (Ingesta unificada de clics, rendimiento, visibilidad y errores)
- `GET /sdk/tracker.js` (Distribución del bundle del cliente)

## 2. Diagrama de Flujo del SDK Empresarial y Enriquecimiento

```mermaid
sequenceDiagram
    autonumber
    actor Web as Navegador del Cliente
    participant SDK as sdk/tracker.js
    participant API as backend/telemetry_controller.py
    participant Enrich as backend/enrichment
    participant DB as database/event_repository.py

    Web->>SDK: Carga de script con data-site-key
    SDK->>API: POST /api/v1/verify { site_key }
    API-->>SDK: 200 OK (Desbloqueo activo)
    
    par Monitoreo Pasivo
        SDK->>Web: Performance API (TTFB, Load Time)
        SDK->>Web: Centinela de Errores (window.onerror)
        SDK->>Web: Visibility State (Tiempo real en pantalla)
    end

    Web->>SDK: Cierre de pestaña / Flush periódico
    SDK->>API: POST /api/v1/telemetry (Lote de eventos)
    Note over API: Extracción rápida de IP y User-Agent
    API->>Enrich: parse_user_agent(headers) + resolve_ip(remote_addr)
    API->>DB: save_batch(eventos_enriquecidos)
    API-->>SDK: 200 OK (stored: N) en < 5ms
```

## 3. Consecuencias
- Desacoplamiento total: el cliente puede actualizar su SDK sin tocar código del backend.
- La base de datos es intercambiable (SQLite a PostgreSQL) modificando únicamente el paquete `database/`.
- Todos los archivos se mantienen estrictamente bajo el límite de 150 líneas.
