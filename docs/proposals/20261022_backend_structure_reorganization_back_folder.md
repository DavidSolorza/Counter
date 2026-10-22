# Propuesta Técnica: Reorganización Estructural del Backend (Carpeta `back/`)

**Fecha:** 22 de Octubre de 2026  
**Autor:** Antigravity Engineering Multi-Agent Team  
**Gobernanza:** Contrato de Gobernanza Técnica v2026.4.0 (< 150 líneas por archivo)

---

## 1. El Qué y el Por Qué

### 1.1 Contexto
El usuario ha solicitado organizar la estructura del Backend separando claramente:
1. **La Librería (`library/` o `sdk/`):** El código JavaScript cliente distribuible (`tracker.js` y sus submódulos de monitoreo de rendimiento, rage clicks, centinela de errores y despachador de beacons).
2. **La Lógica (`logic/` o `src/`):** Todo el motor analítico del servidor, persistencia de base de datos, enriquecimiento GeoIP/User-Agent y controladores de la API REST.
3. **Encapsulamiento en una carpeta `back/`:** Que agrupe ambas partes de manera modular, limpia y directamente conectada al repositorio de Backend.

---

## 2. Arquitectura Propuesta de Directorios

```text
Counter/ (o back/)
├── back/
│   ├── library/                      # 📦 LIBRERÍA CLIENTE DISTRIBUIBLE (SDK)
│   │   ├── tracker.js                # Bundle principal (< 150 líneas)
│   │   └── modules/                  # Módulos atómicos (< 150 líneas c/u)
│   │       ├── handshake.js
│   │       ├── performance_monitor.js
│   │       ├── error_sentinel.js
│   │       ├── visibility_tracker.js
│   │       └── beacon_dispatcher.js
│   │
│   ├── logic/                        # 🧠 LÓGICA DEL SERVIDOR & ANALÍTICA
│   │   ├── core/                     # Configuración, excepciones y rate limiter
│   │   │   ├── config.py
│   │   │   ├── errors.py
│   │   │   └── rate_limiter.py
│   │   ├── database/                 # Persistencia, conexión SQLite y repositorios
│   │   │   ├── connection.py
│   │   │   ├── schemas/              # DDL SQL
│   │   │   └── repositories/         # EventRepository y SiteRepository
│   │   ├── enrichment/               # Procesamiento de red y dispositivo
│   │   │   ├── user_agent_parser.py
│   │   │   └── geo_ip_enricher.py
│   │   ├── analytics/                # Motor de agregaciones y métricas
│   │   │   └── analytics_engine.py
│   │   └── controllers/              # Controladores de endpoints REST
│   │       ├── licensing_controller.py
│   │       └── telemetry_controller.py
│   │
│   ├── app.py                        # Punto de entrada de la API Flask
│   └── tests/                        # Suites de pruebas automatizadas
│       ├── run_tests.py
│       └── test_sdk_resilience.py
│
├── docs/                             # Documentación viva, propuestas y ADRs
├── .gitignore                        # Políticas de exclusión estricta
└── README.md                         # Guía general
```

---

## 3. Beneficios Técnicos
1. **Separación de Responsabilidades Impecable:** La librería que se envía al navegador de los clientes queda físicamente aislada del código de servidor que procesa los datos.
2. **Importaciones Claras y Limpias:** Todo el código Python se referencia de forma coherente (`from back.logic...`).
3. **Mantenimiento y Regla de 150 Líneas:** Cada módulo mantiene su responsabilidad única (SRP) y permanece ampliamente por debajo de las 150 líneas.
