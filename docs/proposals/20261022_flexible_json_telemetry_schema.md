# Propuesta Técnica: Esquema Híbrido Relacional + JSON para Telemetría Flexible

- **Fecha:** 2026-10-22
- **Autor:** Ecosistema Multi-Agente (VP of Engineering & Staff Software Architect & Principal DBA)
- **Estado:** PENDIENTE DE APROBACIÓN (Fase 2 - Ciclo de Gobernanza)
- **Módulo Afectado:** `src/features/analytics/` & `docs/database/`

---

## 1. Contexto y Justificación (El Qué y el Por Qué)

Actualmente, la tabla `telemetry_events` almacena los datos de interacción con una columna rígida `element_target TEXT`. Esta estructura limita la recolección de metadatos enriquecidos (como precios, monedas, atributos personalizados del DOM, coordenadas, selectores anidados o payloads dinámicos) que el SDK de WolfAnalytics o el usuario deseen registrar.

Se propone migrar a un **modelo híbrido Relacional + JSON**:
- En SQLite local: Se utiliza una columna `event_data TEXT` que almacena un objeto JSON estructurado y validado.
- En PostgreSQL (futura fase de producción): Equivalente a `event_data JSONB`.

### Beneficios
1. **Flexibilidad Total:** El SDK puede enviar cualquier objeto arbitrario en `event_data` sin requerir migraciones de base de datos futuras.
2. **Compatibilidad Hacia Atrás:** Si un evento envía el formato anterior con `target`, se encapsula automáticamente dentro de `event_data: { "element": target }`.
3. **Alto Rendimiento:** Inserciones en bloque mediante `executemany` sin overhead de esquemas rígidos.

---

## 2. Impacto Modular y Arquitectura (Vertical Slicing)

Los cambios se aíslan estrictamente en el módulo de analítica sin afectar al módulo de licenciamiento:

1. **Capa Database (`docs/database/002_hybrid_json_schema.sql`):**
   - Actualización de `telemetry_events` reemplazando `element_target` por `event_data TEXT`.
2. **Capa Domain (`src/features/analytics/domain/event_entity.py`):**
   - Modificación de la entidad `TelemetryEvent` para contener `event_data: Dict[str, Any]`.
3. **Capa Application (`src/features/analytics/application/record_events_use_case.py`):**
   - Adaptación para normalizar `event_data` y serializar/validar diccionarios.
4. **Capa Infrastructure (`src/features/analytics/infrastructure/sqlite_event_repository.py`):**
   - Inserción de `json.dumps(event.event_data)` en la columna `event_data`.
5. **SDK Cliente (`src/features/analytics/infrastructure/static/tracker.js`):**
   - Envío de objetos enriquecidos en `event_data` (selectores, texto, dimensiones, atributos custom).
6. **Contratos API (`docs/api/contracts.md`):**
   - Actualización del esquema de carga útil `/api/v1/telemetry`.

---

## 3. Plan de Migración y Auditoría de Líneas

- Todos los archivos modificados permanecerán estrictamente **por debajo de las 150 líneas**.
- Pruebas unitarias actualizadas en `tests/run_tests.py` validando la persistencia y lectura de JSON.
