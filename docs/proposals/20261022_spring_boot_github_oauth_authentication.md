# Propuesta Técnica: Módulo de Autenticación con GitHub (OAuth 2.0) en Spring Boot

- **Fecha:** 2026-10-22
- **Autor:** VP of Engineering & Security Architect
- **Estado:** PENDIENTE DE APROBACIÓN
- **Componente:** `back/spring-security/` (Spring Boot 3.3.5 / Java 25)

---

## 1. Justificación y Objetivos

El Frontend (`Counter-Front`) ha definido el inicio de sesión exclusivo mediante **GitHub OAuth 2.0**.
Para completar el ciclo desacoplado de autenticación sin usar SDKs comerciales pesados (Regla 2.3), el backend de **Spring Boot (Puerto 8080)** debe:

1. Proveer el endpoint `POST /api/v1/auth/github` para recibir el código de autorización (`code`) o el perfil verificado desde el Frontend.
2. Validar la identidad de GitHub consumiendo la API nativa de GitHub (`https://api.github.com/user`) con `java.net.http.HttpClient`.
3. Buscar o registrar automáticamente al usuario y su **Licencia de Counter** (`site_key`) en `security.db`.
4. Retornar el token de sesión, los datos de usuario (`username`, `avatar_url`, `email`, `role`) y la licencia asociada.

---

## 2. Arquitectura de Componentes en Spring Boot

```
back/spring-security/src/main/java/com/counter/security/
├── controller/
│   ├── AuthController.java          # Endpoint POST /api/v1/auth/github (< 80 líneas)
│   └── SecurityController.java      # Handshake de licencias existente (< 80 líneas)
├── service/
│   ├── GithubAuthService.java       # Intercambio OAuth y aprovisionamiento (< 120 líneas)
│   └── SecurityService.java         # Lógica de validación de dominios (< 60 líneas)
├── domain/
│   └── ClientLicense.java           # Entidad JPA vinculada al usuario (< 70 líneas)
└── repository/
    └── LicenseRepository.java       # Repositorio JPA (< 20 líneas)
```

---

## 3. Contrato de API: `POST /api/v1/auth/github`

### Payload de Entrada (desde Counter-Front):
```json
{
  "code": "7a8b9c...",
  "username": "DavidSolorza",
  "avatar_url": "https://github.com/DavidSolorza.png",
  "email": "davidsolorza@github.local",
  "role": "admin"
}
```

### Respuesta Exitosa (`200 OK`):
```json
{
  "success": true,
  "token": "cntr_sess_7f8a9b0c...",
  "user": {
    "username": "DavidSolorza",
    "email": "davidsolorza@github.local",
    "avatar_url": "https://github.com/DavidSolorza.png",
    "role": "admin"
  },
  "license": {
    "site_key": "wk_live_demo",
    "client_name": "DavidSolorza",
    "allowed_domain": "*",
    "is_active": 1
  }
}
```

---

## 4. Garantías de Gobernanza
- Cero SDKs comerciales opacos: uso de `HttpClient` nativo de Java.
- Cada archivo creado o modificado respetará estrictamente el límite de **< 150 líneas**.
