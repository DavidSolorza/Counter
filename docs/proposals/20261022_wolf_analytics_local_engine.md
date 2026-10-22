# Propuesta Técnica: Motor Local de Analítica y Licenciamiento WolfAnalytics (SQLite + Flask)

- **Fecha:** 2026-10-22
- **Autor:** Ecosistema Multi-Agente (Orquestador & Staff Software Architect)
- **Estado:** PENDIENTE DE APROBACIÓN (Fase 2 - Ciclo de Gobernanza)
- **Repositorio:** `https://github.com/DavidSolorza/Counter.git`

---

## 1. Contexto y Objetivos

El objetivo de esta propuesta es implementar una solución modular de analítica web y telemetría ligera ("WolfAnalytics") ejecutada 100% en local mediante **Flask** y persistencia en **SQLite**. 

El sistema implementa un mecanismo estricto de **Handshake / Activación** que bloquea el funcionamiento del SDK del lado del cliente (`tracker.js`) si la llave (`site_key`) no existe, está inactiva o no coincide con los dominios autorizados.

### Metas Específicas
1. **Conexión y Sincronización:** Vinculación al repositorio remoto GitHub `https://github.com/DavidSolorza/Counter.git`.
2. **Arquitectura Vertical Slicing:** Estructurar el código en `src/features/analytics/` y `src/features/licensing/`, respetando POO, Clean Code y el límite inviolable de **150 líneas por archivo**.
3. **Mecanismo Handshake:** Endpoint `/api/v1/verify` que autentica el `site_key`.
4. **Módulo de Telemetría:** Endpoint `/api/v1/telemetry` que recibe eventos en lote (pageviews, clics, tiempos).
5. **SDK Cliente Resistente:** Script modular en JavaScript puro (sin frameworks externos) que solo se activa tras handshake exitoso y envía datos vía `navigator.sendBeacon` o `fetch`.
6. **Entorno de Prueba:** `prueba.html` y el badge interactivo visual (WolfStats) funcionando de forma armónica.

---

## 2. Arquitectura del Sistema (Vertical Slicing)

El proyecto se estructurará siguiendo la gobernanza técnica establecida:

```
Counter/
├── docs/
│   ├── proposals/
│   │   └── 20261022_wolf_analytics_local_engine.md
│   ├── architecture/
│   │   └── ADR-001-local-analytics-architecture.md
│   ├── database/
│   │   └── 001_initial_schema.sql
│   └── api/
│       └── contracts.md
├── src/
│   ├── core/
│   │   ├── config/
│   │   │   └── settings.py              # Variables de entorno y rutas DB (< 150 líneas)
│   │   ├── database/
│   │   │   └── connection.py            # Pool/conexión SQLite tipada (< 150 líneas)
│   │   └── errors/
│   │       └── exceptions.py            # Clases de error de dominio (< 150 líneas)
│   └── features/
│       ├── licensing/
│       │   ├── domain/
│       │   │   ├── site_entity.py       # Modelo POO del Sitio/Licencia (< 150 líneas)
│       │   │   └── repository_interface.py
│       │   ├── application/
│       │   │   └── verify_license_use_case.py (< 150 líneas)
│       │   └── infrastructure/
│       │       ├── sqlite_site_repository.py (< 150 líneas)
│       │       └── licensing_controller.py   # Blueprint Flask /api/v1/verify (< 150 líneas)
│       └── analytics/
│           ├── domain/
│           │   ├── event_entity.py      # Entidad TelemetryEvent (< 150 líneas)
│           │   └── event_repository_interface.py
│           ├── application/
│           │   └── record_events_use_case.py (< 150 líneas)
│           └── infrastructure/
│               ├── sqlite_event_repository.py (< 150 líneas)
│               ├── analytics_controller.py   # Blueprint Flask /api/v1/telemetry (< 150 líneas)
│               └── static/
│                   └── tracker.js       # SDK cliente protegido (< 150 líneas)
├── app.py                               # Entrada Flask y registro de Blueprints (< 150 líneas)
├── prueba.html                          # Suite de prueba local interactiva
└── README.md                            # Documentación viva
```

---

## 3. Estrategia de Bloqueo del SDK (Protección de Licencia)

1. **Estado Latente Inicial:** El SDK se carga con atributo `data-site-key="wk_test_12345"`.
2. **Petición Handshake:** Se emite un `POST /api/v1/verify`.
3. **Filtro de Seguridad:**
   - Si la respuesta es `403` o `valid: false`: el SDK emite una advertencia discreta y finaliza su hilo de ejecución sin enlazar ningún event listener ni enviar telemetría.
   - Si la respuesta es `200` y `valid: true`: se instancian los interceptores de clics, scroll y `beforeunload`.

---

## 4. Impacto y Beneficios

- **Cero Acoplamiento:** Negocio aislado de frameworks (POO pura en `domain/` y `application/`).
- **Mantenibilidad:** Cada clase y controlador tiene una única responsabilidad y nunca excede las 150 líneas.
- **Rendimiento:** Base de datos SQLite local sin latencia de red externa ni overhead de infraestructura.
- **Trazabilidad:** Git inicializado y vinculado al repositorio GitHub oficial.
