# ADR-004: Estrategia de Flush Oportuno y Dashboard de Inspección

- **Estado:** PROPUESTO
- **Fecha:** 2026-10-22
- **Decisores:** Staff Software Architect & VP of Engineering

## 1. Decisión de Diseño

Se adopta una estrategia de despacho híbrida en el SDK:
- **Interval Flush (4 segundos):** Un temporizador recurrente vacía el buffer si contiene elementos.
- **Immediate Flush:** Para eventos críticos de alta prioridad (errores JS y excepciones no capturadas).
- **Page Unload Flush:** `visibilitychange` (a `hidden`), `pagehide` y `beforeunload` como respaldo final.
- **Feedback Visual (Console + Dashboard):** El SDK emite logs legibles en modo depuración y el backend expone `/dashboard` para ver las métricas sin necesidad de hacer queries manuales SQL.

## 2. Diagrama de Flujo

```mermaid
sequenceDiagram
    autonumber
    actor User as Usuario en PruebaCouter (Vite :5173)
    participant SDK as tracker.js
    participant API as Backend Flask (:5000)
    participant Dash as /dashboard

    User->>SDK: Carga de página / Acciones en la UI
    Note over SDK: Buffer temporal en memoria (clics, navegación)
    
    rect rgb(230, 245, 230)
    Note over SDK: Temporizador de 4s expira CON eventos en buffer
    SDK->>API: POST /api/v1/telemetry (Lote de eventos)
    API-->>SDK: 200 OK (stored: N)
    Note over SDK: Imprime en consola: [WolfAnalytics:Sync] N eventos enviados
    end

    alt Error JavaScript Ocurrido
        User->>SDK: window.onerror
        SDK->>API: POST /api/v1/telemetry (Flush Inmediato)
    end

    API->>Dash: Eventos visibles en tiempo real (< 2s)
```
