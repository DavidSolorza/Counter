# Propuesta Técnica: Integración Multi-Proveedor con Google OAuth 2.0

**Fecha:** 2026-10-22  
**Autor:** Agente 4 (Ingeniero de Backend) & Agente 2 (Arquitecto)  
**Estado:** APROBADO / EJECUTADO  
**Módulos Impactados:** `back/spring-security/`, `Counter-Front/`

---

## 1. Contexto y Justificación

Tras la incorporación exitosa de la autenticación con GitHub en Spring Boot, se requirió habilitar federación de identidades complementaria con **Google OAuth 2.0**.

El objetivo es proveer paridad total con GitHub:
1. Intercambio seguro del código de autorización contra los servidores oficiales de Google (`https://oauth2.googleapis.com/token`).
2. Consulta de información de perfil del usuario (`https://www.googleapis.com/oauth2/v3/userinfo`).
3. Creación y resolución automática de la licencia B2B (`cntr_google_<usuario>_...`) en la base de datos `security.db`.
4. Emisión de tokens de sesión unificados (`cntr_googlesess_...`) e integración limpia con el frontend React.

---

## 2. Arquitectura de la Solución

- **Servicio Nativo (`GoogleAuthService.java`):**
  - Implementación con `java.net.http.HttpClient` sin SDKs comerciales de terceros (Regla 2.3).
  - Manejo seguro de Client ID y Client Secret.
  - Generación de claves de sitio aisladas y cuotas independientes por cliente Google.
- **Controlador Multi-Proveedor (`AuthController.java`):**
  - Exposición del endpoint `POST /api/v1/auth/google`.
  - Endpoint de salud `/api/v1/auth/health` reportando `providers: ["github", "google"]`.
- **Integración Frontend (`google_auth_service.ts`):**
  - Comunicación fluida con el backend vía `httpClient.post`.
  - Almacenamiento seguro de tokens y `site_key` en `localStorage`.
