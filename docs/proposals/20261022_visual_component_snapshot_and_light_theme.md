# Propuesta Técnica: Captura Visual de Componentes (DOM Snapshots Inertes) y Modo Claro

- **Fecha:** 2026-10-22
- **Autor:** Ecosistema Multi-Agente (VP of Engineering & Staff Software Architect)
- **Estado:** PENDIENTE DE APROBACIÓN (Fase 2 - Ciclo de Gobernanza)
- **Repositorio:** `https://github.com/DavidSolorza/Counter.git`

---

## 1. Contexto y Objetivos (El Qué y el Por Qué)

El usuario ha solicitado dos evoluciones visuales y funcionales clave:

1. **Recreación Visual de Componentes Interactuados (DOM Snapshots Inertes):**
   - Cuando un visitante interactúa con un elemento en la web del cliente (botón, imagen, tarjeta o video), el SDK extrae metadatos visuales ligeros (~40 bytes) sin enviar archivos multimedia pesados:
     - **Botón / Enlace:** Color de fondo (`backgroundColor`), color de texto (`color`), radio del borde (`borderRadius`) y texto visible.
     - **Imagen (`<img>`):** Texto alternativo (`alt`), ancho y alto (`width x height`).
     - **Video (`<video>` o `<iframe>`):** Dimensiones y ratio con placeholder interactivo inerte.
     - **Tarjeta (`.card` o contenedor):** Título interior y estilos de contorno.
   - En el Dashboard de Counter se renderiza una réplica miniatura visual **completamente inerte** (`pointer-events: none`), permitiendo al cliente identificar inmediatamente el elemento exacto sin interpretar códigos técnicos.

2. **Transición a Modo Claro (Light Theme):**
   - Rediseño de la interfaz visual del Dashboard ([backend/dashboard.html](file:///c:/Users/Usuario/Desktop/Counter/backend/dashboard.html)) hacia una paleta clara, moderna y limpia:
     - Fondos: `#f8fafc` (Slate claro) y tarjetas en `#ffffff`.
     - Tipografía de alto contraste: `#0f172a` y texto atenuado en `#64748b`.
     - Bordes sutiles `#e2e8f0` con sombras suaves de elevación.
     - Badges de color legibles sobre fondo claro.

---

## 2. Impacto Modular y Gobernanza (< 150 Líneas)

- **SDK (`sdk/tracker.js`):** Función de extracción visual `extractVisualSnapshot(el)` en < 20 líneas, manteniendo el archivo total en < 110 líneas.
- **Dashboard (`backend/dashboard.html`):** Estilos CSS en modo claro y función de renderizado de la miniatura inerte en < 125 líneas.
- **Tests (`tests/`):** Pruebas de integración actualizadas verificando la persistencia de metadatos `visual`.
