# ADR-011: Arquitectura de Microservicios Dual (Spring Boot Security + Flask Analytics)

**Estado:** Propuesto  
**Fecha:** 22 de Octubre de 2026  
**Contexto de Decisión:** Segregación de responsabilidades entre seguridad/licencias y procesamiento/ingesta de telemetría.

---

## 1. Contexto y Problema

Centralizar la validación de licencias y el procesamiento masivo de eventos en un solo proceso de servidor puede generar cuellos de botella y riesgos de disponibilidad. Si una oleada de eventos de telemetría satura el servicio de ingesta, las peticiones críticas de autenticación y verificación de licencias de nuevos clientes podrían degradarse o fallar.

---

## 2. Decisión de Arquitectura

1. **Microservicio de Seguridad (`back/spring-security/`):**
   - Desarrollado con Spring Boot (Java 25).
   - Base de datos aislada: `security.db` (SQLite).
   - Expone `POST /api/v1/security/verify` en el puerto 8080 para validar llaves, dominios autorizados y estado activo (Kill Switch).
2. **Microservicio de Analítica (`back/flask-analytics/`):**
   - Desarrollado con Flask (Python 3.13).
   - Base de datos aislada: `analytics.db` (SQLite).
   - Expone `POST /api/v1/telemetry/collect` y `GET /api/v1/analytics/summary/<site_key>` en el puerto 5000.
3. **Orquestación en la Librería Cliente (`back/library/tracker.js`):**
   - Handshake inicial asíncrono hacia el puerto 8080.
   - Si la respuesta es exitosa, inicializa los listeners y despacha eventos hacia el puerto 5000.
   - Si la respuesta es 403 o la llave es inválida, se apaga de inmediato sin emitir eventos.

---

## 3. Consecuencias

- **Positivas:**
  - Resiliencia y escalabilidad independiente para cada servicio.
  - Blindaje empresarial para la lógica de monetización y licencias.
  - Mayor facilidad para integrar futuras pasarelas de pago o webhooks en el servicio de seguridad.
- **Negativas / Mitigaciones:**
  - Requiere levantar dos procesos en desarrollo local (8080 y 5000). Se proveerá un script orquestador para iniciar ambos con un solo comando.
