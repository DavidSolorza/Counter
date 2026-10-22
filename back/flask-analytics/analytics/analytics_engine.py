"""
back/flask-analytics/analytics/analytics_engine.py
Motor analítico para el cálculo de métricas agregadas en analytics.db.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any, List

try:
    from database.connection import db, AnalyticsDatabaseManager
except ImportError:
    from ..database.connection import db, AnalyticsDatabaseManager


class AnalyticsEngine:
    def __init__(self, manager: AnalyticsDatabaseManager = db) -> None:
        self._manager = manager

    def get_summary(self, site_key: str) -> Dict[str, Any]:
        with self._manager.session() as conn:
            c = conn.cursor()

            # 1. Conteo total de eventos
            c.execute("SELECT COUNT(*) AS total FROM telemetry_events WHERE site_key = ?;", (site_key,))
            total_events = c.fetchone()["total"]

            # 2. Conteo por tipo de evento
            c.execute("""
                SELECT event_type, COUNT(*) AS count
                FROM telemetry_events
                WHERE site_key = ?
                GROUP BY event_type;
            """, (site_key,))
            type_counts = {row["event_type"]: row["count"] for row in c.fetchall()}

            # 3. Top páginas visitadas
            c.execute("""
                SELECT page_url, COUNT(*) AS count
                FROM telemetry_events
                WHERE site_key = ?
                GROUP BY page_url
                ORDER BY count DESC
                LIMIT 5;
            """, (site_key,))
            top_pages = [{"url": r["page_url"], "views": r["count"]} for r in c.fetchall()]

            # 4. Top elementos clickeados (json_extract nativo)
            c.execute("""
                SELECT json_extract(event_data, '$.element') AS element, COUNT(*) AS clicks
                FROM telemetry_events
                WHERE site_key = ? AND event_type IN ('click', 'rage_click')
                AND json_extract(event_data, '$.element') IS NOT NULL
                GROUP BY element
                ORDER BY clicks DESC
                LIMIT 5;
            """, (site_key,))
            top_elements = [{"element": r["element"], "clicks": r["clicks"]} for r in c.fetchall()]

            # 5. Desglose de dispositivos
            c.execute("""
                SELECT json_extract(event_data, '$._client.device') AS device, COUNT(*) AS count
                FROM telemetry_events
                WHERE site_key = ? AND json_extract(event_data, '$._client.device') IS NOT NULL
                GROUP BY device;
            """, (site_key,))
            devices = {r["device"]: r["count"] for r in c.fetchall()}

            # 6. Distribución de scroll milestones
            c.execute("""
                SELECT json_extract(event_data, '$.depth') AS depth, COUNT(*) AS count
                FROM telemetry_events
                WHERE site_key = ? AND event_type = 'scroll_milestone'
                GROUP BY depth;
            """, (site_key,))
            scroll_data = {r["depth"]: r["count"] for r in c.fetchall()}

            return {
                "site_key": site_key,
                "total_events": total_events,
                "total_clicks": type_counts.get("click", 0),
                "rage_clicks": type_counts.get("rage_click", 0),
                "errors_count": type_counts.get("client_error", 0) + type_counts.get("promise_rejection", 0),
                "web_vitals_count": type_counts.get("web_vitals", 0),
                "top_pages": top_pages,
                "top_elements": top_elements,
                "devices": devices,
                "scroll_milestones": scroll_data
            }


analytics_engine = AnalyticsEngine()
