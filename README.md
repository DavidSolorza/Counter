# 🐺 WolfAnalytics Engine & Licensing Gateway

Motor de analítica ligero y pasarela de validación de licencias para sitios web, desarrollado con **Flask** y **SQLite** bajo arquitectura **Vertical Slicing** y gobernanza técnica estricta.

---

## 🚀 Inicio Rápido en Local

### 1. Requisitos Previos
- Python 3.10+
- Paquetes instalados:
  ```bash
  pip install Flask flask-cors
  ```

### 2. Ejecución del Servidor
```bash
python app.py
```
- API Base: `http://127.0.0.1:5000/api/v1`
- SDK Cliente: `http://127.0.0.1:5000/tracker.js`
- Suite de Prueba Local: `http://127.0.0.1:5000/test`

### 3. Ejecución de Pruebas
```bash
python tests/run_tests.py
```

---

## 🛡️ Mecanismo de Bloqueo del SDK

1. El SDK (`tracker.js`) busca su `data-site-key` (ej. `wk_test_12345`).
2. Realiza un Handshake inicial contra `POST /api/v1/verify`.
3. **Si la llave no existe o `is_active = 0`:** El SDK entra en modo silenciado, no intercepta clics, no mide eventos y muestra un aviso en consola.
4. **Si la llave es válida:** Se activa el recolector de eventos y transmite vía `navigator.sendBeacon` o `fetch` al endpoint `/api/v1/telemetry`.

---

## 📁 Estructura del Proyecto
- `docs/`: Propuestas técnicas, diagramas Mermaid (ADR) y contratos de API.
- `src/core/`: Configuración, conexión SQLite y cliente HTTP nativo.
- `src/features/licensing/`: Dominio, casos de uso y endpoints de validación de licencias.
- `src/features/analytics/`: Dominio, casos de uso, repositorios y SDK estático.
- `prueba.html`: Página interactiva de demostración con badge visual.
