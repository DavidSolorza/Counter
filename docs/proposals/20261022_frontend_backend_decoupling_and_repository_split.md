# Propuesta Técnica: Desacoplamiento Total de Repositorios (Backend vs Frontend)

**Fecha:** 22 de Octubre de 2026  
**Autor:** Antigravity Engineering Multi-Agent Team  
**Gobernanza:** Contrato de Gobernanza Técnica v2026.4.0 (< 150 líneas por archivo)

---

## 1. El Qué y el Por Qué

### 1.1 Contexto
El usuario ha solicitado una separación física y arquitectónica total entre el Backend y el Frontend de **Counter**:
- El repositorio actual ([DavidSolorza/Counter.git](https://github.com/DavidSolorza/Counter.git)) albergará exclusivamente el **Backend**:
  - Lógica de extracción y análisis de telemetría (`backend/`, `src/`).
  - Capa de persistencia y base de datos relacional (`database/`).
  - Librería SDK cliente distribuible (`sdk/tracker.js` y submódulos).
  - Pruebas automatizadas y contratos de API.
  - Su archivo `.gitignore` excluirá todo artefacto, build o código de frontend.
- Un nuevo repositorio independiente ([DavidSolorza/Counter-Front.git](https://github.com/DavidSolorza/Counter-Front.git)) albergará exclusivamente el **Frontend**:
  - Landing Page oficial de Counter (presentación, documentación y descarga del SDK).
  - Dashboard de Inteligencia Empresarial en Modo Claro con Recreación Visual de Componentes.
  - Comunicación estrictamente desacoplada mediante llamadas HTTP a la API REST (`/api/v1/verify`, `/api/v1/telemetry`, `/api/v1/analytics/summary`, `/api/v1/events`).
  - Su archivo `.gitignore` excluirá cualquier archivo de backend (`*.py`, `*.db`, `*.sqlite`, `__pycache__`, etc.).

---

## 2. Plan de Implementación

### 2.1 Repositorio Backend (`Counter`)
1. **Configuración de `.gitignore`:**
   - Bloquear y excluir directorios de interfaz gráfica desacoplada (`frontend/`, `client/`, `web/`, `dist/`, `PruebaCouter/`).
   - Mantener las rutas de entrega del SDK (`/sdk/tracker.js`, `/download/counter.js`) y endpoints REST.
2. **Higiene de Git:**
   - Confirmar que ningún archivo temporal de front quede trackeado.

### 2.2 Repositorio Frontend (`Counter-Front`)
1. **Ubicación Local:**
   - Se creará en `C:\Users\Usuario\Desktop\Counter-Front` como repositorio Git independiente.
2. **Estructura Modular (< 150 líneas por archivo):**
   - `index.html`: Landing Page corporativa y descarga de SDK.
   - `dashboard.html`: Panel analítico en Modo Claro con widgets de métricas y wireframing de componentes.
   - `styles/main.css`: Estilos visuales en Modo Claro.
   - `scripts/api_client.js`: Cliente HTTP nativo para consumir la API de Counter.
   - `.gitignore`: Exclusión total de backend (`*.py`, `*.db`, `__pycache__`, etc.) y dependencias de node.
   - `README.md`: Documentación de integración con la API del backend.
3. **Sincronización:**
   - Inicializar `git init`, vincular `origin https://github.com/DavidSolorza/Counter-Front.git`, rama `main`, commit y push inicial.

---

## 3. Beneficios Técnicos
1. **Desacoplamiento Absoluto:** El frontend puede desplegarse en Vercel, Netlify, Cloudflare Pages o AWS S3/CloudFront sin depender del entorno Python.
2. **Seguridad y Superficie de Ataque Reducida:** El frontend no tiene acceso al sistema de archivos ni credenciales de base de datos; solo consume endpoints públicos protegidos.
3. **Escalabilidad de Equipos:** Permite versionar, probar y desplegar frontend y backend en ciclos independientes.
