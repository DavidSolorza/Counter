"""
back/flask-analytics/analytics/visual_wireframe.py
Reconstrucción de componentes DOM interactuados a partir de metadatos visuales.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any, List
import json

try:
    from database.connection import db, AnalyticsDatabaseManager
except ImportError:
    from ..database.connection import db, AnalyticsDatabaseManager


class VisualWireframeProcessor:
    def __init__(self, manager: AnalyticsDatabaseManager = db) -> None:
        self._manager = manager

    def get_components_gallery(self, site_key: str, limit: int = 8) -> List[Dict[str, Any]]:
        with self._manager.session() as conn:
            c = conn.cursor()

            # Obtener el total de clics para calcular porcentaje de interacción
            c.execute("""
                SELECT COUNT(*) AS total_clicks
                FROM telemetry_events
                WHERE site_key = ? AND event_type IN ('click', 'rage_click');
            """, (site_key,))
            tot = c.fetchone()["total_clicks"] or 1

            # Agrupar elementos con metadatos visuales válidos
            c.execute("""
                SELECT 
                    json_extract(event_data, '$.element') AS element,
                    json_extract(event_data, '$.text') AS text,
                    json_extract(event_data, '$.visual.type') AS visual_type,
                    json_extract(event_data, '$.visual.bg') AS bg,
                    json_extract(event_data, '$.visual.color') AS color,
                    json_extract(event_data, '$.visual.radius') AS radius,
                    COUNT(*) AS clicks
                FROM telemetry_events
                WHERE site_key = ? 
                  AND event_type IN ('click', 'rage_click')
                  AND json_extract(event_data, '$.text') IS NOT NULL
                  AND json_extract(event_data, '$.text') != ''
                GROUP BY text, element, bg
                ORDER BY clicks DESC
                LIMIT ?;
            """, (site_key, limit))

            components = []
            for row in c.fetchall():
                clicks = row["clicks"]
                pct = round((clicks / tot * 100), 1)
                components.append({
                    "element": row["element"] or "button",
                    "text": row["text"],
                    "visual_type": row["visual_type"] or "button",
                    "styles": {
                        "backgroundColor": row["bg"] or "rgba(241, 245, 249, 0.9)",
                        "color": row["color"] or "rgb(15, 23, 42)",
                        "borderRadius": row["radius"] or "8px"
                    },
                    "total_clicks": clicks,
                    "engagement_share": pct
                })

            return components


visual_processor = VisualWireframeProcessor()
