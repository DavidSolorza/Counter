# Manual de Usuario y Guía de Integración: Plataforma Counter

Bienvenido a **Counter**, la solución integral de analítica web, telemetría en tiempo real y monitoreo de salud web para aplicaciones de alto rendimiento.

---

## 1. Instalación Rápida

Para integrar Counter en cualquier sitio web o aplicación (React, Vite, Next.js, HTML estático o WordPress), añade el siguiente fragmento en la etiqueta `<head>` o justo antes del cierre de `</body>`:

```html
<!-- Counter Analytics SDK -->
<script src="http://127.0.0.1:5000/counter.js" data-site-key="wk_test_12345" async></script>
```

### Opciones de Configuración (Atributos del `<script>`):
- `data-site-key` (Obligatorio): Clave de activación única de tu dominio (Ej: `wk_test_12345`).
- `data-debug` (Opcional): Si se establece en `"true"`, emite trazas detalladas en la consola del navegador.
- `data-api-base` (Opcional): URL personalizada del backend si no se encuentra en el origen por defecto.

---

## 2. ¿Cómo Funciona la API? (Qué se manda y cómo se envía)

Counter opera bajo una arquitectura de **dos pasos sincronizados**:

### Paso 1: El Handshake de Activación (`POST /api/v1/verify`)
- **Qué envía:** `{ "site_key": "wk_test_12345" }`
- **Cómo lo envía:** Una petición rápida `fetch` asíncrona al cargar la página.
- **Respuesta:** Si la clave está activa y coincide con el dominio, el servidor responde con `200 OK`. Si la clave es inválida, el servidor devuelve `403 Forbidden` y el SDK se silencia por completo (no registra clics ni consume memoria).

### Paso 2: Ingesta de Telemetría en Lote (`POST /api/v1/telemetry`)
- **Qué envía:** Un lote (batch) de eventos estructurados en JSON:
```json
{
  "site_key": "wk_test_12345",
  "events": [
    {
      "event_type": "click",
      "page_url": "https://midominio.com/catalogo",
      "event_data": {
        "element": "BUTTON#btn-comprar",
        "text": "Comprar Plan"
      }
    }
  ]
}
```
- **Cómo lo envía:**
  - **En navegación activa:** Petición `POST` con `fetch({ keepalive: true })` cada 4 segundos o mediante debounce al interactuar.
  - **Al salir de la página:** Mediante `navigator.sendBeacon`, garantizando que ningún evento se pierda cuando el usuario cierra la pestaña.
- **Enriquecimiento en Servidor:** El backend extrae la IP real y analiza la cabecera `User-Agent`, añadiendo automáticamente metadatos de navegador, sistema operativo y red a cada evento sin invadir la privacidad.

---

## 3. Disparo de Eventos Personalizados

Puedes enviar tus propios eventos de negocio (compras, conversiones, registros) mediante la API global:

```javascript
// En cualquier script de tu frontend:
if (window.Counter) {
    window.Counter.track('compra', {
        plan: 'Netflix Premium 4K',
        precio: 45.00,
        moneda: 'COP',
        metodo_pago: 'Nequi'
    });
}
```

---

## 4. Centinela de Errores y Web Vitals

Counter monitorea automáticamente:
1. **Errores de JavaScript:** Captura cualquier excepción no controlada (`window.onerror`) o promesa rechazada y la reporta al dashboard inmediatamente para alertar al equipo de desarrollo.
2. **Web Vitals (Navigation Timing):** Mide TTFB (tiempo hasta el primer byte) y tiempo total de carga de la página.
3. **Filtro de Privacidad (PII Shield):** Omite automáticamente contraseñas, tarjetas de crédito o campos con el atributo `data-private`.

---

## 5. Portal y Dashboard en Vivo

Accede a `http://127.0.0.1:5000/dashboard` para supervisar la telemetría en tiempo real, descargar la librería actualizada (`counter.js`) o consultar asistencia técnica.
