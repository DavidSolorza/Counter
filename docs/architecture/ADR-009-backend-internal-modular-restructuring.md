# ADR-009: Reestructuración Modular Interna del Backend (`back/library` y `back/logic`)

**Estado:** Propuesto  
**Fecha:** 22 de Octubre de 2026  
**Contexto de Decisión:** Organización física del Backend en módulos dedicados para la librería cliente (`library/`) y el motor de procesamiento del servidor (`logic/`).

---

## 1. Contexto y Problema

Actualmente en el repositorio de Backend coexisten en la raíz varias carpetas técnicas (`backend/`, `database/`, `sdk/`, `src/`). Para lograr máxima claridad y mantenibilidad, se requiere consolidar todo el backend bajo un contenedor `back/` con dos ramas principales:
1. `back/library/`: El código JavaScript distribuible del SDK que se ejecuta en los clientes.
2. `back/logic/`: Todo el código Python de persistencia, analítica, controladores y configuración del servidor.

---

## 2. Decisión de Arquitectura

1. **Creación del paquete raíz `back/`:**
   - Centraliza el ciclo de vida del servicio analítico.
2. **Aislamiento de la Librería (`back/library/`):**
   - Agrupa `tracker.js` y `modules/`. Servido mediante streaming estático en las rutas `/counter.js` y `/download/counter.js`.
3. **Consolidación de la Lógica (`back/logic/`):**
   - Agrupa `core/`, `database/`, `enrichment/`, `analytics/` y `controllers/`.
4. **Punto de Entrada (`back/app.py`):**
   - Inicializa la base de datos, registra los Blueprints de `back.logic.controllers` y expone los servicios REST.
5. **Gobernanza de Líneas de Código:**
   - Se mantiene la regla estricta de < 150 líneas por archivo en toda la jerarquía.

---

## 3. Consecuencias

- **Positivas:**
  - Estructura intuitiva y predecible.
  - Elimina la dispersión de carpetas en la raíz.
  - Facilita empaquetar o dockerizar el backend como una unidad única.
- **Ajustes Requeridos:**
  - Actualización de los imports Python (`from back.logic...`).
  - Actualización de rutas en las suites de prueba (`tests/run_tests.py` y `tests/test_sdk_resilience.py`).
