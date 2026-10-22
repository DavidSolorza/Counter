"""
back/flask-analytics/analytics/funnel_processor.py
Cálculo de embudos de conversión y tasas de abandono (drop-off).
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any, List

try:
    from database.connection import db, AnalyticsDatabaseManager
except ImportError:
    from ..database.connection import db, AnalyticsDatabaseManager


class FunnelProcessor:
    def __init__(self, manager: AnalyticsDatabaseManager = db) -> None:
        self._manager = manager

    def calculate_funnel(self, site_key: str) -> List[Dict[str, Any]]:
        with self._manager.session() as conn:
            c = conn.cursor()

            # Paso 1: Visita inicial (Todas las sesiones únicas)
            c.execute("""
                SELECT COUNT(DISTINCT json_extract(event_data, '$._sid')) AS count
                FROM telemetry_events
                WHERE site_key = ?;
            """, (site_key,))
            s1 = c.fetchone()["count"] or 0

            # Paso 2: Exploración (Filtros, Catálogo o Scroll >= 25%)
            c.execute("""
                SELECT COUNT(DISTINCT json_extract(event_data, '$._sid')) AS count
                FROM telemetry_events
                WHERE site_key = ? AND (
                    event_type = 'scroll_milestone' OR
                    (event_type = 'click' AND (
                        json_extract(event_data, '$.text') LIKE '%Películas%' OR
                        json_extract(event_data, '$.text') LIKE '%Series%' OR
                        json_extract(event_data, '$.text') LIKE '%Todas%' OR
                        json_extract(event_data, '$.element') LIKE '%catalog%'
                    ))
                );
            """, (site_key,))
            s2 = c.fetchone()["count"] or 0

            # Paso 3: Intención de compra (Clic en Añadir / Carrito / ¡Añadido!)
            c.execute("""
                SELECT COUNT(DISTINCT json_extract(event_data, '$._sid')) AS count
                FROM telemetry_events
                WHERE site_key = ? AND (
                    json_extract(event_data, '$.text') LIKE '%Añadido%' OR
                    json_extract(event_data, '$.text') LIKE '%Comprar%' OR
                    json_extract(event_data, '$.text') LIKE '%Agregar%' OR
                    json_extract(event_data, '$.element') LIKE '%btn-cart%'
                );
            """, (site_key,))
            s3 = c.fetchone()["count"] or 0

            # Paso 4: Cierre / Conversión (Soporte / WhatsApp / Checkout)
            c.execute("""
                SELECT COUNT(DISTINCT json_extract(event_data, '$._sid')) AS count
                FROM telemetry_events
                WHERE site_key = ? AND (
                    json_extract(event_data, '$.text') LIKE '%Soporte%' OR
                    json_extract(event_data, '$.text') LIKE '%WhatsApp%' OR
                    json_extract(event_data, '$.element') LIKE '%whatsapp%'
                );
            """, (site_key,))
            s4 = c.fetchone()["count"] or 0

            steps_data = [
                ("1. Visita y Entrada", s1),
                ("2. Exploración Catálogo", min(s2, s1)),
                ("3. Intención de Compra", min(s3, s1)),
                ("4. Contacto y Conversión", min(s4, s1))
            ]

            result = []
            prev = s1
            for idx, (label, count) in enumerate(steps_data):
                conv_rate = round((count / s1 * 100), 1) if s1 > 0 else 0.0
                drop_off = round(((prev - count) / prev * 100), 1) if prev > 0 and idx > 0 else 0.0
                result.append({
                    "step": idx + 1,
                    "name": label,
                    "sessions": count,
                    "conversion_rate": conv_rate,
                    "drop_off_rate": drop_off
                })
                prev = count

            return result


funnel_processor = FunnelProcessor()
