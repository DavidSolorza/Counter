# Propuesta Técnica: Procesamiento Avanzado de Datos en Flask y Visualización en Frontend

- **Fecha:** 2026-10-22
- **Autor:** VP of Engineering & Staff Software Architect
- **Estado:** PENDIENTE DE APROBACIÓN
- **Repositorios Involucrados:** `Counter` (Backend Flask) y `Counter-Front` (Frontend React)

---

## 1. Justificación y Objetivos

Con la ingesta dual-microservice validada (más de 45 eventos capturados en vivo desde `http://localhost:5175/`), el siguiente salto de ingeniería consiste en **transformar los datos crudos de SQLite en inteligencia de negocio procesada y representarla visualmente de forma ordenada en el Dashboard React**.

### Objetivos Clave:
1. **Embudos de Conversión (Funnels):** Analizar el flujo del visitante (Home ➔ Filtro de Categoría ➔ Clic en Carrito / WhatsApp ➔ Checkout).
2. **Diagnóstico de Fricción (Rage Clicks y Errores):** Agrupar los clics de frustración y los errores de React capturados en el cliente.
3. **Galería de Wireframes Visuales:** Recrear en el Dashboard los componentes reales clicados con sus colores, estilos y texto exactos.
4. **Métricas de Sesión Reales:** Calcular tasa de rebote (*Bounce Rate*), permanencia activa y páginas por sesión.
5. **Consumo en Frontend (`Counter-Front`):** Reemplazar los mocks estáticos en React por el consumo en vivo de la API analítica.

---

## 2. Arquitectura Backend (Flask - Puerto 5000)

Se crearán submódulos especializados en `back/flask-analytics/analytics/`, garantizando el límite de **< 150 líneas por archivo**:

```
back/flask-analytics/analytics/
├── funnel_processor.py     # Análisis de pasos y tasas de abandono (< 120 líneas)
├── friction_analyzer.py    # Detección y agrupamiento de Rage Clicks y errores (< 120 líneas)
├── visual_wireframe.py     # Extracción y firma visual de componentes DOM (< 110 líneas)
├── session_metrics.py      # Duración activa, rebote y sesiones únicas (< 110 líneas)
└── analytics_engine.py     # Orquestador del endpoint /api/v1/analytics/overview (< 130 líneas)
```

### Nuevo Endpoint Unificado:
`GET /api/v1/analytics/overview/<site_key>`:
Entrega una estructura consolidada con KPIs reales, pasos del embudo, galería visual y feed reciente de eventos.

---

## 3. Arquitectura Frontend (`Counter-Front` - React)

En `Counter-Front/src/features/analytics/`:
1. **Selector de Site Key:** Permitir alternar entre `wk_live_demo` (tienda en vivo) y `wk_test_12345`.
2. **KPI Ribbon:** Tarjetas vivas con sesiones, clics totales, tasa de rebote y tiempo medio.
3. **Funnel Visualizer:** Barra progresiva mostrando la caída de usuarios paso a paso.
4. **Wireframe Renderer:** Muestra visual de los botones clicados (con su `bg`, `color` y `border-radius`).
5. **Centro de Fricción:** Tabla de alertas con los errores de React y rage clicks detectados.
6. **Tabla de Eventos Vivos:** Sustituye los datos mockeados por el streaming real de la API.

---

## 4. Plan de Ejecución

1. **Paso 1 (Backend):** Crear los 4 procesadores en Flask y exponer `/api/v1/analytics/overview/<site_key>`.
2. **Paso 2 (Validación API):** Verificar con pruebas automatizadas en Flask que los 45 eventos de `wk_live_demo` se procesan con latencia < 10 ms.
3. **Paso 3 (Frontend):** Actualizar `Counter-Front` para conectar los servicios y componentes React a la API real.
4. **Paso 4 (Auditoría):** Revisar en navegador (`http://localhost:5174/`) y verificar 0 errores y < 150 líneas por archivo.
