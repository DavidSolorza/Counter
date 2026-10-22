# ADR-010: Sistema B2B de Licenciamiento, Domain Locking y Kill-Switch Remoto

**Estado:** Propuesto  
**Fecha:** 22 de Octubre de 2026  
**Contexto de Decisión:** Protección de propiedad intelectual, control de suscripciones y prevención de suplantación de dominios en Counter.

---

## 1. Contexto y Problema

El SDK cliente se distribuye públicamente para ser incrustado en sitios web. Sin una vinculación criptográfica o contextual de dominio (*Domain Locking*) y expiración, un tercero podría copiar la `site_key` de un cliente y consumirla en dominios no autorizados, distorsionando las analíticas y evadiendo el pago de suscripciones.

---

## 2. Decisión de Arquitectura

1. **Bloqueo por Dominio Multivalor:**
   - Cada registro de `sites` almacena una lista de dominios autorizados separados por coma (ej. `tienda.com, dev.tienda.com, localhost, 127.0.0.1`).
   - El backend normaliza el host entrante (eliminando puertos) y valida pertenencia.
2. **Ciclo de Suscripción con Expiración Temporal:**
   - Columna `expires_at` evaluada contra `CURRENT_TIMESTAMP` en el motor de base de datos.
3. **Mecanismo de Kill-Switch Bidireccional:**
   - **Handshake Inicial:** El SDK envía el hostname actual en `/api/v1/verify`. Si la respuesta no es `valid: true`, la ejecución del SDK se aborta sin adjuntar event listeners.
   - **Ingesta de Telemetría:** El endpoint `/api/v1/telemetry` valida nuevamente el origen para prevenir peticiones forjadas por bots o curl.

---

## 3. Consecuencias

- **Positivas:**
  - Control riguroso de monetización B2B.
  - Mitigación completa de robo de scripts.
  - Compatibilidad transparente con entornos locales (`localhost`, `127.0.0.1`) y producción.
- **Negativas / Mitigaciones:**
  - En pruebas locales que usen dominios custom (ej. `mi-app.test`), el dominio debe registrarse previamente en la base de datos o consola de licencias.
