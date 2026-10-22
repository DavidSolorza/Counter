# ADR-008: Desacoplamiento Físico de Repositorios (Backend vs Frontend)

**Estado:** Propuesto  
**Fecha:** 22 de Octubre de 2026  
**Contexto de Decisión:** Separación estricta de responsabilidades entre el servicio de análisis de datos y la interfaz de usuario.

---

## 1. Contexto y Problema

Inicialmente, el backend servía plantillas HTML embebidas para propósitos de prueba rápida y demostración. Para escalar a un ecosistema empresarial limpio y seguro, se requiere aislar la interfaz de usuario (Dashboard y Landing Page) en un repositorio independiente ([Counter-Front](https://github.com/DavidSolorza/Counter-Front.git)) y conservar en el repositorio principal ([Counter](https://github.com/DavidSolorza/Counter.git)) únicamente el motor analítico, la persistencia y la librería SDK.

---

## 2. Decisión de Arquitectura

1. **Separación de Repositorios:**
   - **`Counter.git` (Backend):** Contiene la lógica de extracción, enriquecimiento (GeoIP, User-Agent), endpoints REST `/api/v1/`, base de datos SQLite y el SDK distribuible `counter.js`.
   - **`Counter-Front.git` (Frontend):** Contiene la Landing Page oficial, el Dashboard de inteligencia en Modo Claro y el cliente de conexión a la API HTTP.
2. **Contrato de Comunicación Exclusivo:**
   - No existe importación ni referencia directa de código entre ambos proyectos. La única interfaz de integración es el protocolo HTTP/JSON a través de `http://127.0.0.1:5000/api/v1` (o la URL de producción configurada).
3. **Alineación de `.gitignore`:**
   - Cada repositorio tendrá una política estricta de exclusión:
     - Backend ignora directorios de front y builds cliente.
     - Frontend ignora archivos Python, bases de datos SQLite y cachés de ejecución.

---

## 3. Consecuencias

- **Positivas:**
  - Despliegue independiente (ej. frontend estático en CDN y backend en contenedor/servidor).
  - Cumplimiento riguroso del principio de responsabilidad única (SRP).
  - Facilidad de mantenimiento y gobernanza de código.
- **Negativas / Mitigaciones:**
  - Requiere habilitar CORS para los orígenes del frontend (ya configurado en `backend/app.py`).
