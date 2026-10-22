# ADR-001: Arquitectura de Analítica Local y Validación de Llaves

- **Estado:** PROPUESTO
- **Fecha:** 2026-10-22
- **Decisores:** Staff Software Architect & VP of Engineering

## 1. Decisión de Diseño

Se adopta una arquitectura basada en **Vertical Slicing** y **Clean Architecture / Hexagonal** con separación estricta en tres capas por módulo:
- `domain`: Reglas de negocio e interfaces sin dependencias de librerías externas.
- `application`: Casos de uso específicos orquestando las transacciones.
- `infrastructure`: Controladores Flask, adaptadores SQLite y assets del cliente.

## 2. Diagrama de Flujo del Handshake y Telemetría

```mermaid
sequenceDiagram
    autonumber
    actor User as Navegador Cliente
    participant SDK as tracker.js (SDK)
    participant API as Flask Backend (/api/v1)
    participant DB as SQLite (local_analytics.db)

    User->>SDK: Carga de script con data-site-key
    SDK->>API: POST /api/v1/verify { site_key }
    API->>DB: SELECT * FROM sites WHERE site_key = ? AND is_active = 1
    alt Licencia Invalida o Inactiva
        DB-->>API: No match / is_active = 0
        API-->>SDK: 403 Forbidden { valid: false }
        Note over SDK: BLOQUEO TOTAL.<br/>Se aborta ejecución.<br/>Cero listeners registrados.
    else Licencia Valida
        DB-->>API: Registro de Sitio Activo
        API-->>SDK: 200 OK { valid: true, domain: "..." }
        Note over SDK: DESBLOQUEO.<br/>Registra pageview.<br/>Activa interceptores de clics.
    end

    User->>SDK: Interacción (Clic, Navegación, Salida)
    Note over SDK: Acumula eventos en buffer en memoria
    User->>SDK: Evento beforeunload / Cierre de página
    SDK->>API: POST /api/v1/telemetry (navigator.sendBeacon)
    API->>DB: INSERT INTO telemetry_events (batch)
    API-->>SDK: 200 OK { stored: N }
```

## 3. Diagrama de Componentes

```mermaid
graph TD
    subgraph Client ["Cliente Web"]
        HTML["prueba.html"]
        Tracker["tracker.js (SDK Protegido)"]
        HTML --> Tracker
    end

    subgraph Server ["Backend Flask (Vertical Slices)"]
        App["app.py (Factory / Runner)"]
        
        subgraph LicensingFeature ["Feature: Licensing"]
            L_Ctrl["licensing_controller.py"]
            L_UC["verify_license_use_case.py"]
            L_Repo["sqlite_site_repository.py"]
            L_Ctrl --> L_UC --> L_Repo
        end

        subgraph AnalyticsFeature ["Feature: Analytics"]
            A_Ctrl["analytics_controller.py"]
            A_UC["record_events_use_case.py"]
            A_Repo["sqlite_event_repository.py"]
            A_Ctrl --> A_UC --> A_Repo
        end

        App --> L_Ctrl
        App --> A_Ctrl
    end

    subgraph Storage ["Persistencia"]
        DB[(local_analytics.db)]
        L_Repo --> DB
        A_Repo --> DB
    end
```

## 4. Consecuencias
- **Límite de líneas:** Cada clase de repositorio, caso de uso y controlador no supera las 70-110 líneas.
- **Independencia de pruebas:** Los casos de uso pueden probarse unitariamente sustituyendo los repositorios mediante contratos (interfaces).
