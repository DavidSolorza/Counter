# Propuesta Técnica: Arquitectura de Tokens Privados y Blindaje Anti-Fraude en Spring Boot

- **Fecha:** 2026-10-22
- **Autor:** VP of Engineering & Security Architect
- **Estado:** PENDIENTE DE APROBACIÓN
- **Componente:** `back/spring-security/` (Spring Boot 3.3.5 / Java 25)

---

## 1. Justificación y Problema de Seguridad

En plataformas SaaS de telemetría (como Stripe, Cloudflare o Counter), la **Site Key** que va en el HTML del cliente es necesariamente pública para que el navegador descargue el script. 

### El Riesgo de Fraude:
Si un tercero malintencionado inspecciona el código fuente de un cliente legítimo, podría copiar la `site_key` e incrustarla en su propia web para:
1. Consumir la cuota de eventos del cliente que paga.
2. Contaminar las analíticas con tráfico basura o ataques bot.

---

## 2. Solución de Blindaje Anti-Fraude (Arquitectura B2B)

Implementaremos un esquema de **Doble Token y Validación Criptográfica en Spring Boot**:

```mermaid
graph TD
    subgraph CLIENTE ["Cliente B2B"]
        HTML["Script en HTML (Public Key: cntr_pub_...)"]
        Dashboard["Panel Privado (Secret Key: cntr_sec_...)"]
    end

    subgraph SPRING ["Spring Boot :8080 (Seguridad)"]
        Inspector["Validador de Cabeceras Protegidas (Origin / Referer)"]
        TokenIssuer["Emisor de Session Token Temporal (HMAC)"]
        DB[("security.db (client_licenses)")]
    end

    subgraph FLASK ["Flask :5000 (Analítica)"]
        Collector["Colector Protegido (Verifica Session Token)"]
    end

    HTML -->|1. Handshake con Origin forzado| Inspector
    Inspector -->|2. Valida Dominio Exacto| DB
    Inspector -->|3. Genera Token Temporal (2h)| TokenIssuer
    TokenIssuer -->|4. Retorna Session Token| HTML
    HTML -->|5. Lotes con Token Temporal| Collector
    Dashboard -->|Administración / Rotación de Llaves| DB
```

---

## 3. Pilares Anti-Fraude a Implementar en Spring Boot

### 1. Par de Llaves Criptográficas (Public + Secret)
- **`site_key` (Pública):** Formato `cntr_pub_[hash]`. Va en el `<script>`.
- **`secret_key` (Privada):** Formato `cntr_sec_[hash]`. NUNCA va en el HTML. Solo la conoce el cliente para ingresar al dashboard, rotar su clave pública o cambiar dominios.

### 2. Validación de Cabeceras Protegidas (`Origin` y `Referer`)
El navegador impide que JavaScript modifique los encabezados `Origin` y `Referer`. Spring Boot validará que la petición provenga obligatoriamente de los dominios autorizados registrados por el cliente. Si un sitio pirata usa la llave, `Origin` reportará el dominio del pirata y Spring Boot bloqueará la llamada con `403 Forbidden`.

### 3. Emisión de Token Temporal Firmado (`session_token`)
Spring Boot firmará un pase de telemetría efímero (HMAC-SHA256, válido por 2 horas). Flask únicamente aceptará lotes que contengan este pase firmado, impidiendo que bots ataquen a Flask directamente.

### 4. Rotación Inmediata de Llaves (*Key Rolling*)
Si el cliente sospecha que su llave fue comprometida, puede llamar a `/api/v1/security/licenses/regenerate` con su `secret_key` y generar una nueva Site Key en 1 segundo.

---

## 4. Cambios en Base de Datos (`security.db`)
Se agregarán a `client_licenses`:
- `client_email`: Correo del cliente (único).
- `secret_key`: Token privado de administración (`cntr_sec_...`).
- `monthly_quota`: Límite mensual de eventos contratados (ej. 100,000).
- `tier`: Plan (`starter`, `pro`, `enterprise`).
