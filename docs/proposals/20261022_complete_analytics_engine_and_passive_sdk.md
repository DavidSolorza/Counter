# Propuesta Técnica: Telemetría Pasiva de Máxima Densidad (SDK) y Motor de Inteligencia Agregada (Backend)

- **Fecha:** 2026-10-22
- **Autor:** Ecosistema Multi-Agente (VP of Engineering & Staff Software Architect)
- **Estado:** PENDIENTE DE APROBACIÓN (Fase 2 - Ciclo de Gobernanza)
- **Repositorio:** `https://github.com/DavidSolorza/Counter.git`

---

## 1. Contexto y Objetivos (El Qué y el Por Qué)

El usuario ha seleccionado la **Opción 3 (Completa)** bajo un mandato de rendimiento intransigente: **"que ni se sienta que está en función, pero recolectando la máxima cantidad de datos posibles"**.

### A. Mejoras en la Librería (`sdk/`) con Cero Latencia
1. **Scroll Throttled & Passive Listeners:**
   - Detección de hitos de profundidad (25%, 50%, 75%, 100%) utilizando `{ passive: true }` y `requestAnimationFrame`. Cero bloqueo del compositor de renderizado.
2. **Detección de Fricción ("Rage Clicks"):**
   - Detector en memoria de ráfagas de clics (≥3 clics en <800ms sobre el mismo elemento), catalogándolo como evento crítico de UX.
3. **Atribución Completa de Marketing:**
   - Extracción automática de parámetros `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content` y `document.referrer`.
4. **Contexto de Hardware y Conexión:**
   - Lectura no bloqueante de `navigator.connection.effectiveType` (4G/3G/WiFi), `navigator.language` y dimensiones de viewport.
5. **Session ID Efímero:**
   - Asignación de UUID de sesión en `sessionStorage` para vincular todo el recorrido de un usuario en una misma visita sin usar cookies invasivas.

### B. Motor de Inteligencia y Agregaciones en Backend (`backend/`)
1. **Motor de Agregación (`backend/analytics/analytics_engine.py`):**
   - Agrupación por sesiones para calcular:
     - Tasa de Rebote (*Bounce Rate*): Sesiones con 1 sola página y < 10s de atención.
     - Top de Elementos más Clickeados y Páginas más visitadas.
     - Detección de Fricción (conteo de *Rage Clicks* totales).
     - Salud del Sistema (tasa de errores JS por cada 100 visitas).
2. **Endpoint de Inteligencia (`GET /api/v1/analytics/summary/<site_key>`):**
   - Retorna métricas procesadas y agregadas para alimentar gráficos interactivos en el Dashboard.
3. **Dashboard Visual Enriquecido:**
   - Gráficos de barras nativos CSS/SVG para distribución de dispositivos, top páginas y embudos de interacción.

---

## 2. Garantía de Gobernanza (< 150 Líneas por Archivo)
- `sdk/tracker.js` y submódulos se mantendrán modulares y estrictamente < 150 líneas.
- `backend/analytics/analytics_engine.py` concentrará las consultas analíticas en < 110 líneas.
- `backend/dashboard.html` se actualizará con métricas agregadas visuales en < 150 líneas.
