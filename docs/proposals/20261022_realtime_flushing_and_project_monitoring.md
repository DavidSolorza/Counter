# Propuesta Técnica: Sincronización en Tiempo Real, Dashboard de Monitoreo e Integración en PruebaCouter

- **Fecha:** 2026-10-22
- **Autor:** Ecosistema Multi-Agente (VP of Engineering & Staff Software Architect)
- **Estado:** PENDIENTE DE APROBACIÓN (Fase 2 - Ciclo de Gobernanza)
- **Repositorio:** `https://github.com/DavidSolorza/Counter.git`

---

## 1. Contexto y Objetivos (El Qué y el Por Qué)

El usuario requiere:
1. **Transparencia y Oportunidad en el Envío de Datos ("cuando es"):**
   - Actualmente, el buffer acumulaba eventos hasta el cierre de la página (`beforeunload`), lo que retrasaba la visibilidad de los datos en la base de datos.
   - Se implementará una estrategia de envío oportuna:
     - **Interval Flush:** Sincronización automática periódica (cada 4 segundos) si hay eventos en buffer.
     - **Debounced Flush:** Tras interacción del usuario, vaciado automático con debounce de 1 segundo.
     - **Modo Debug:** Atributo `data-debug="true"` que imprime en la consola del navegador la emisión y respuesta del servidor (`[WolfAnalytics:Sent] 3 eventos transmitidos [200 OK]`).
2. **Dashboard Visual en Vivo (`/dashboard`):**
   - Panel de control integrado en el backend Flask que muestra una vista tabular en tiempo real de los eventos ingresados, sus metadatos (`_client`, `_network`, `event_data`) y métricas de Web Vitals.
3. **Instalación y Monitoreo en Proyecto Grande (`PruebaCouter`):**
   - Inyección del script SDK en `PruebaCouter/index.html`.
   - Autorización del dominio de desarrollo de Vite (`localhost:5173` o comodín `*`) en la base de datos para garantizar handshake exitoso.
   - Confirmación de exclusión en `.gitignore` para no subir `PruebaCouter/` a GitHub.

---

## 2. Plan de Implementación y Auditoría de Líneas

1. **SDK (`sdk/tracker.js` & `sdk/modules/beacon_dispatcher.js`):**
   - Incorporación de timer de sincronización periódica y logs en consola con `data-debug`. (< 150 líneas).
2. **Backend (`backend/controllers/telemetry_controller.py` & `backend/app.py`):**
   - Endpoint `/dashboard` para visualización en tiempo real. (< 150 líneas).
3. **Base de Datos (`database/schemas/001_initial_schema.sql`):**
   - Inserción de autorización de comodín o puertos locales (`localhost:*`). (< 150 líneas).
4. **Proyecto `PruebaCouter`:**
   - Inyección en `PruebaCouter/index.html`.
