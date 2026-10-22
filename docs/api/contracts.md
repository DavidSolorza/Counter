# Contratos de API: WolfAnalytics Service

- **Versión:** 1.0.0
- **Base URL:** `http://127.0.0.1:5000/api/v1`
- **Formato:** JSON (`application/json`)

---

## 1. Verificación de Licencia (Handshake)

Verifica si la `site_key` enviada por el SDK cliente está activa y autorizada para recolectar datos.

- **Método:** `POST`
- **Ruta:** `/verify`
- **Cabeceras:** `Content-Type: application/json`

### Request Body
```json
{
  "site_key": "wk_test_12345"
}
```

### Respuestas

#### `200 OK` (Licencia Válida)
```json
{
  "valid": true,
  "message": "Licencia activa. SDK desbloqueado.",
  "domain": "localhost"
}
```

#### `403 Forbidden` (Licencia Inválida, Inactiva o No Proporcionada)
```json
{
  "valid": false,
  "error": "Licencia inválida o inactiva. SDK bloqueado."
}
```

---

## 2. Ingesta de Telemetría

Recibe un lote de eventos capturados por el SDK cliente.

- **Método:** `POST`
- **Ruta:** `/telemetry`
- **Cabeceras:** `Content-Type: application/json` (o `text/plain` enviado por `navigator.sendBeacon`)

### Request Body
```json
{
  "site_key": "wk_test_12345",
  "events": [
    {
      "type": "pageview",
      "target": "Mi Web de Prueba",
      "url": "http://127.0.0.1:5000/test"
    },
    {
      "type": "click",
      "target": "BUTTON#btn-comprar",
      "url": "http://127.0.0.1:5000/test"
    }
  ]
}
```

### Respuestas

#### `200 OK` (Ingesta Exitosa)
```json
{
  "success": true,
  "stored": 2
}
```

#### `400 Bad Request` (Payload malformado)
```json
{
  "error": "El payload debe contener site_key y una lista de eventos válida."
}
```

#### `403 Forbidden` (Llave de sitio no autorizada)
```json
{
  "error": "Unauthorized: Invalid key"
}
```

---

## 3. Servidor de Assets Estáticos

- **Ruta:** `/tracker.js` (GET) - Entrega el script del SDK para inclusión vía `<script src="http://127.0.0.1:5000/tracker.js" ...>`
- **Ruta:** `/test` (GET) - Entrega la interfaz de demostración interactiva (`prueba.html`)
