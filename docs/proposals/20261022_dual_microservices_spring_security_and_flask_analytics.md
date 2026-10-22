# Propuesta Técnica: Arquitectura de Microservicios Dual (Spring Boot Security + Flask Analytics)

**Fecha:** 22 de Octubre de 2026  
**Autor:** Antigravity Engineering Multi-Agent Team  
**Gobernanza:** Contrato de Gobernanza Técnica v2026.4.0 (< 150 líneas por archivo)

---

## 1. El Qué y el Por Qué

### 1.1 Contexto
El usuario ha propuesto una evolución arquitectónica de 10 fases para estructurar el backend de **Counter** en dos microservicios especializados e independientes:
1. **Microservicio de Seguridad y Licencias (Spring Boot / Java - Puerto 8080):**
   - Responsabilidad exclusiva: Autenticación de Site Keys, Domain Locking, validación de estado activo (`is_active` / Kill Switch) y generación segura de llaves comerciales.
   - Base de datos aislada: `security.db` (SQLite).
2. **Microservicio de Analítica y Telemetría (Flask / Python - Puerto 5000):**
   - Responsabilidad exclusiva: Ingesta masiva asíncrona de eventos, almacenamiento en JSON flexible, enriquecimiento de red/dispositivo y motor de cálculo de métricas para el Dashboard.
   - Base de datos aislada: `analytics.db` (SQLite).
3. **Librería Cliente SDK (`tracker.js`):**
   - Orquesta el flujo: ejecuta el Handshake inicial contra Spring Boot (8080) y, tras la aprobación, despacha los datos a Flask (5000).

---

## 2. Mapa de Integración y Adaptación (10 Fases)

| Fase | Título | Adaptación a Nuestro Código Actual |
| :--- | :--- | :--- |
| **Fase 1** | Entorno Local & SQLite | Crear `back/spring-security/` y `back/flask-analytics/` con `security.db` y `analytics.db`. |
| **Fase 2** | Esquemas de BD Aislados | `client_licenses` en `security.db` e índices; `telemetry_events` en `analytics.db` con JSON. |
| **Fase 3** | Núcleo Spring Boot | Proyecto Spring Boot con Spring Data JPA y SQLite JDBC (`sqlite-jdbc`). |
| **Fase 4** | Handshake & Kill Switch | Endpoint `POST /api/v1/security/verify` (8080) con Domain Locking y CORS. |
| **Fase 5** | Núcleo Flask | Migrar nuestro motor existente a `back/flask-analytics/` con `/health` (5000). |
| **Fase 6** | Ingesta Flexible Flask | Endpoint `POST /api/v1/telemetry/collect` serializando JSON y respuesta 200 rápida. |
| **Fase 7** | SDK Dual | Actualizar `tracker.js` para validar en 8080 y reportar en 5000 con `sendBeacon`. |
| **Fase 8** | Integración del Flujo | Orquestación simultánea de ambos microservicios y verificación con `prueba.html`. |
| **Fase 9** | Dashboard Local | Exponer `/api/v1/analytics/summary` en Flask y verificar enlace con `Counter-Front`. |
| **Fase 10** | Pruebas de Blindaje | Tests de Kill Switch (is_active=0), llaves falsas y dominios no autorizados. |

---

## 3. Estructura de Carpetas Propuesta

```text
Counter/ (DavidSolorza/Counter.git)
├── back/
│   ├── spring-security/              # 🛡️ Microservicio 1: Seguridad (Spring Boot / 8080)
│   │   ├── pom.xml                   # Dependencias Web, JPA, SQLite
│   │   ├── security.db               # Base de datos de licencias
│   │   └── src/main/java/com/counter/security/
│   │       ├── CounterSecurityApp.java
│   │       ├── domain/ClientLicense.java
│   │       ├── repository/LicenseRepository.java
│   │       ├── service/SecurityService.java
│   │       └── controller/SecurityController.java
│   │
│   ├── flask-analytics/              # 📊 Microservicio 2: Analítica (Flask / 5000)
│   │   ├── analytics.db              # Base de datos de telemetría
│   │   ├── app.py                    # Entrypoint Flask
│   │   ├── core/                     # config, errors, rate_limiter
│   │   ├── database/                 # connection, schemas, event_repository
│   │   ├── enrichment/               # geo_ip_enricher, user_agent_parser
│   │   ├── analytics/                # analytics_engine
│   │   └── controllers/              # telemetry_controller
│   │
│   └── library/                      # 📦 SDK Distribuible (tracker.js)
│       ├── tracker.js                # Handshake en 8080 + Telemetría en 5000
│       └── modules/
│
├── docs/                             # Documentación, propuestas y ADRs
├── .gitignore                        # Políticas estrictas
└── README.md                         # Guía de orquestación dual
```

---

## 4. Beneficios Técnicos
1. **Seguridad Robusta B2B en Java:** La lógica crítica de negocio, licencias y tokens queda blindada en un entorno fuertemente tipado (Spring Data JPA).
2. **Ingesta y Analítica Rápida en Python:** El procesamiento de telemetría y consultas JSON aprovecha la flexibilidad y ligereza de Flask.
3. **Cero Acoplamiento:** Los microservicios no comparten base de datos ni memoria; si el backend de analítica se satura, el de seguridad continúa autenticando sin interrupciones.
