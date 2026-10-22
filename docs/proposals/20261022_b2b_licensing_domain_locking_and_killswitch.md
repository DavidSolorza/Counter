# Propuesta Técnica: Sistema de Licenciamiento B2B, Domain Locking y Kill-Switch Remoto

**Fecha:** 22 de Octubre de 2026  
**Autor:** Antigravity Engineering Multi-Agent Team  
**Gobernanza:** Contrato de Gobernanza Técnica v2026.4.0 (< 150 líneas por archivo)

---

## 1. El Qué y el Por Qué

### 1.1 Contexto
Para consolidar **Counter** como una plataforma B2B monetizable y segura, se requiere robustecer el sistema de llaves de activación (`Site Keys`) para evitar:
- Copia no autorizada o robo de scripts en dominios ajenos (*script theft*).
- Uso del servicio tras el vencimiento del periodo de facturación mensual.
- Sobrecarga no autorizada en el backend por clientes suspendidos o fraudulentos.

### 1.2 Objetivos de la Mejora
1. **Domain Locking (Bloqueo por Dominio):** La Site Key solo es válida si la petición proviene del dominio autorizado registrado (o lista de dominios permitidos, ej. `tiendadezapatos.com, localhost, 127.0.0.1`).
2. **Fecha de Expiración (`expires_at`):** Control del ciclo de vida de la suscripción (mensual/anual) y plan (`plan_tier`).
3. **Kill-Switch Remoto en SDK y Backend:** Si la llave no coincide con el dominio o la licencia expiró, la API responde `403 Forbidden` y el SDK se apaga de inmediato sin inicializar escuchas ni consumir recursos.

---

## 2. Plan de Implementación

### 2.1 Base de Datos (`back/logic/database/`)
- Migración `003_licensing_domain_locking.sql`:
  - Agrega columnas `expires_at TIMESTAMP` y `plan_tier TEXT DEFAULT 'pro'`.
  - Configura el sitio semilla de prueba con expiración a 1 año y soporte para `localhost,127.0.0.1`.

### 2.2 Repositorio de Sitios (`site_repository.py`)
- Método `validate_license(site_key, client_domain)` que verifica en una sola consulta:
  - Existencia y estado activo (`is_active == 1`).
  - No expiración (`expires_at IS NULL OR expires_at >= CURRENT_TIMESTAMP`).
  - Coincidencia estricta o comodín con los dominios autorizados.

### 2.3 Controlador de Licencias (`licensing_controller.py`)
- El endpoint `/api/v1/verify` recibe `{ site_key, domain }` y cabeceras `Origin`/`Referer`.
- Devuelve `{ valid: true, domain, plan_tier, expires_at }` o `{ valid: false, error: "..." }` con código 403.

### 2.4 Controlador de Telemetría (`telemetry_controller.py`)
- Valida la licencia y el origen en el endpoint `/api/v1/telemetry` para rechazar ingestas si el dominio es suplantado.

### 2.5 SDK Cliente (`back/library/tracker.js`)
- En el handshake envía automáticamente `window.location.hostname`.
- Si `res.valid` es falso, activa el Kill-Switch silenciando el SDK.

---

## 3. Beneficios Técnicos y de Negocio
- **Monetización Garantizada:** Los clientes no pueden revender ni duplicar el script en múltiples sitios web.
- **Preparado para Webhooks de Pasarelas (ePayco/Stripe):** Permite activar o suspender licencias automáticamente tras pagos o cancelaciones.
- **Gobernanza:** Todos los archivos permanecen estrictamente por debajo de las 150 líneas.
