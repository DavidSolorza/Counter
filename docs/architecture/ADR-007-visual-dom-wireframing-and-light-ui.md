# ADR-007: Wireframing Visual Inerte de Componentes y Modo Claro

- **Estado:** PROPUESTO
- **Fecha:** 2026-10-22
- **Decisores:** Staff Software Architect & UI/UX Designer

## 1. Decisión de Diseño

1. **Aislamiento de Componentes Recreados:**
   - La réplica del componente en el Dashboard se renderiza con `pointer-events: none` y estilos encapsulados para evitar colisiones con el CSS del panel.
   - En ningún caso se descargan imágenes pesadas ni se ejecutan scripts embebidos en el elemento.

2. **Diseño de Interfaz en Modo Claro:**
   - Se reemplaza la paleta oscura por una escala clara de alto contraste (WCAG AAA):
     - Superficie base: `#f8fafc`
     - Superficie de tarjetas: `#ffffff`
     - Límites y divisores: `#e2e8f0`
     - Acentos interactivos: `#2563eb` (Azul corporativo) y `#16a34a` (Verde esmeralda).

## 2. Diagrama de Flujo

```mermaid
graph LR
    User[Interacción en tienda cliente] --> Inspect[Extracción 5 tokens CSS < 0.1ms]
    Inspect --> JSON[Objeto liviano: { visual: { tag, bg, color, text, dims } }]
    JSON --> Ingest[Backend /api/v1/telemetry]
    Ingest --> DB[(SQLite JSON)]
    DB --> Render[Dashboard Modo Claro]
    Render --> Wireframe[Maniquí Visual Inerte: pointer-events: none]
```
