# Contratos de API: WolfAnalytics Service

- **Versión:** 1.1.0
- **Base URL:** `http://127.0.0.1:5000/api/v1`
- **Formato:** JSON (`application/json`)

---

## 1. Verificación de Licencia (Handshake)

Verifica si la `site_key` enviada por el SDK cliente está activa y autorizada para recolectar datos.

- **Método:** `POST`
- **Ruta:** `/verify`

### Request Body
```json
{
  "site_key": "wk_test_12345"
}
```

### Respuestas
- `200 OK`: `{"valid": true, "message": "Licencia activa. SDK desbloqueado.", "domain": "localhost"}`
- `403 Forbidden`: `{"valid": false, "error": "Licencia inválida o inactiva. SDK bloqueado."}`

---

## 2. Ingesta de Telemetría Flexible (Esquema Híbrido)

Recibe un lote de eventos con objetos dinámicos variables en `event_data`.

- **Método:** `POST`
- **Ruta:** `/telemetry`

### Request Body
```json
{
  "site_key": "wk_test_12345",
  "events": [
    {
      "event_type": "click",
      "page_url": "http://127.0.0.1:5000/test",
      "event_data": {
        "element": "button#btn-comprar",
        "price": 45.00,
        "currency": "USD",
        "custom_attr": "promo_verano"
      }
    }
  ]
}
```

### Respuestas
- `200 OK`: `{"success": true, "stored": 1}`
- `400 Bad Request`: `{"error": "Payload de telemetría inválido o malformado."}`
- `403 Forbidden`: `{"error": "Unauthorized: Invalid key"}`
