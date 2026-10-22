"""
back/flask-analytics/analytics/analytics_engine.py
Orquestador principal de analítica avanzada para Counter Analytics.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any

try:
    from database.connection import db, AnalyticsDatabaseManager
    from analytics.funnel_processor import funnel_processor
    from analytics.friction_analyzer import friction_analyzer
    from analytics.visual_wireframe import visual_processor
    from analytics.session_metrics import session_calculator
except ImportError:
    from ..database.connection import db, AnalyticsDatabaseManager
    from .funnel_processor import funnel_processor
    from .friction_analyzer import friction_analyzer
    from .visual_wireframe import visual_processor
    from .session_metrics import session_calculator


class AnalyticsEngine:
    def __init__(self, manager: AnalyticsDatabaseManager = db) -> None:
        self._manager = manager

    def get_overview(self, site_key: str) -> Dict[str, Any]:
        """Genera el informe analítico completo consolidado para el Frontend."""
        kpis = session_calculator.get_session_kpis(site_key)
        funnel = funnel_processor.calculate_funnel(site_key)
        friction = friction_analyzer.get_friction_report(site_key)
        visuals = visual_processor.get_components_gallery(site_key, limit=8)

        return {
            "site_key": site_key,
            "kpis": kpis,
            "funnel": funnel,
            "friction": friction,
            "visual_components": visuals
        }

    def get_summary(self, site_key: str) -> Dict[str, Any]:
        """Resumen rápido para compatibilidad retroactiva."""
        with self._manager.session() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) AS total FROM telemetry_events WHERE site_key = ?;", (site_key,))
            tot = c.fetchone()["total"]

            c.execute("SELECT event_type, COUNT(*) AS count FROM telemetry_events WHERE site_key = ? GROUP BY event_type;", (site_key,))
            type_counts = {r["event_type"]: r["count"] for r in c.fetchall()}

            c.execute("""
                SELECT json_extract(event_data, '$.element') AS element, COUNT(*) AS clicks
                FROM telemetry_events
                WHERE site_key = ? AND event_type IN ('click', 'rage_click')
                  AND json_extract(event_data, '$.element') IS NOT NULL
                GROUP BY element ORDER BY clicks DESC LIMIT 5;
            """, (site_key,))
            top_elements = [{"element": r["element"], "clicks": r["clicks"]} for r in c.fetchall()]

            return {
                "site_key": site_key,
                "total_events": tot,
                "total_clicks": type_counts.get("click", 0),
                "rage_clicks": type_counts.get("rage_click", 0),
                "errors_count": type_counts.get("client_error", 0) + type_counts.get("promise_rejection", 0),
                "top_elements": top_elements
            }


analytics_engine = AnalyticsEngine()
