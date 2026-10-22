# Propuesta Técnica: Reestructuración Modular Tripartita y SDK Empresarial (Performance, Errores y Enriquecimiento)

- **Fecha:** 2026-10-22
- **Autor:** Ecosistema Multi-Agente (VP of Engineering & Staff Software Architect)
- **Estado:** PENDIENTE DE APROBACIÓN (Fase 2 - Ciclo de Gobernanza)
- **Repositorio:** `https://github.com/DavidSolorza/Counter.git`

---

## 1. Contexto y Objetivos (El Qué y el Por Qué)

El usuario ha solicitado evolucionar la solución hacia un sistema empresarial con dos ejes fundamentales:

1. **Separación Modular Tripartita Estricta:**
   - **`sdk/` (Librería del Cliente):** Código frontend modular que el cliente descarga. Contiene el núcleo de inicialización con handshake, centinela de errores, monitor de Performance Web Vitals y observador de visibilidad.
   - **`backend/` (Servidor y API):** Backend en Flask enfocado en responder en < 5ms mediante buffer/cola en memoria, enriqueciendo cada evento con metadatos del visitante (User-Agent nativo, IP/GeoIP).
   - **`database/` (Persistencia):** Scripts SQL, migraciones y adaptadores de conexión (SQLite con compatibilidad PostgreSQL).
   - **Punto de Conexión Unificado:** Todo el SDK interactúa exclusivamente a través de los endpoints estándar `/api/v1/verify` (handshake) y `/api/v1/telemetry` (ingesta multipropósito de métricas, clics y errores).

2. **Capacidades Empresariales del SDK:**
   - **Performance API (`window.performance`):** Captura métricas críticas (TTFB, DOM Content Loaded, tiempo total de carga).
   - **Centinela de Errores Frontend (`onerror` y `unhandledrejection`):** Detección proactiva de fallos en la web del cliente.
   - **Visibility State API & Intersection Observer:** Control exacto de tiempo activo (descartando pestañas en segundo plano) y visibilidad de elementos clave.
   - **Enriquecimiento en Backend:** Clasificación automática de navegadores/dispositivos (Mobile/Desktop/OS) y extracción de IP de origen sin ralentizar la respuesta HTTP.

---

## 2. Mapa Arquitectónico Propuesto

```
Counter/
├── sdk/                                # 1. Toda la librería cliente que descarga el usuario
│   ├── modules/
│   │   ├── handshake.js                # Validación y estado activo (< 150 líneas)
│   │   ├── performance_monitor.js      # Métricas de carga TTFB/Navigation (< 150 líneas)
│   │   ├── error_sentinel.js           # Captura window.onerror (< 150 líneas)
│   │   ├── visibility_tracker.js       # Control de pestaña activa (< 150 líneas)
│   │   └── beacon_dispatcher.js        # Envío batch sendBeacon (< 150 líneas)
│   └── tracker.js                      # Bundle orquestador unificado distribuible (< 150 líneas)
├── backend/                            # 2. Toda la lógica del servidor y enriquecimiento
│   ├── core/                           # Configuración y manejo de excepciones
│   ├── enrichment/
│   │   ├── user_agent_parser.py        # Detección pura de SO y Navegador (< 150 líneas)
│   │   └── geo_ip_enricher.py          # Extracción y resolución de IP (< 150 líneas)
│   ├── queue/
│   │   └── memory_event_buffer.py      # Buffer concurrente no bloqueante (< 150 líneas)
│   ├── controllers/
│   │   ├── licensing_controller.py     # Endpoint /api/v1/verify (< 150 líneas)
│   │   └── telemetry_controller.py     # Endpoint /api/v1/telemetry unificado (< 150 líneas)
│   └── app.py                          # Servidor principal Flask (< 150 líneas)
├── database/                           # 3. Toda la persistencia y esquemas
│   ├── schemas/
│   │   ├── 001_initial_schema.sql      # Tablas base (< 150 líneas)
│   │   └── 002_hybrid_json_schema.sql  # Esquema JSON flexible (< 150 líneas)
│   ├── connection.py                   # Administrador transaccional (< 150 líneas)
│   └── repositories/
│       ├── site_repository.py          # Repositorio de sitios (< 150 líneas)
│       └── event_repository.py         # Repositorio de eventos en lote (< 150 líneas)
├── docs/                               # Gobernanza y documentación
├── tests/                              # Suite de pruebas unitarias
└── prueba.html                         # Suite de demostración interactiva
```

---

## 3. Beneficios y Mitigación de Rendimiento

- **Cero Bloqueo en Frontend:** Las métricas de rendimiento y errores se procesan en segundo plano (`requestIdleCallback` o eventos pasivos) sin afectar el tiempo de renderizado de la web del cliente.
- **Respuesta Rápida en Backend:** El controlador enriquece y almacena en buffer en milisegundos, respondiendo `200 OK` inmediatamente.
- **Mantenibilidad Extrema:** Modificar la librería, el backend o la base de datos se realiza en directorios aislados sin mezclar tecnologías.
