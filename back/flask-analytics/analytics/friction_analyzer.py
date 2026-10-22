"""
back/flask-analytics/analytics/friction_analyzer.py
Diagnóstico de fricción de experiencia (Rage Clicks y Errores de cliente).
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any, List

try:
    from database.connection import db, AnalyticsDatabaseManager
except ImportError:
    from ..database.connection import db, AnalyticsDatabaseManager


class FrictionAnalyzer:
    def __init__(self, manager: AnalyticsDatabaseManager = db) -> None:
        self._manager = manager

    def get_friction_report(self, site_key: str) -> Dict[str, Any]:
        with self._manager.session() as conn:
            c = conn.cursor()

            # 1. Agrupación de Rage Clicks
            c.execute("""
                SELECT 
                    json_extract(event_data, '$.element') AS element,
                    json_extract(event_data, '$.text') AS text,
                    MAX(json_extract(event_data, '$.clicks')) AS max_clicks,
                    COUNT(*) AS occurrences,
                    json_extract(event_data, '$.visual') AS visual
                FROM telemetry_events
                WHERE site_key = ? AND event_type = 'rage_click'
                GROUP BY element, text
                ORDER BY occurrences DESC
                LIMIT 10;
            """, (site_key,))
            rage_items = []
            for r in c.fetchall():
                rage_items.append({
                    "element": r["element"] or "Desconocido",
                    "text": r["text"] or "",
                    "max_clicks_recorded": r["max_clicks"] or 3,
                    "incidents": r["occurrences"],
                    "visual": r["visual"]
                })

            # 2. Agrupación de Errores de Frontend
            c.execute("""
                SELECT 
                    json_extract(event_data, '$.message') AS message,
                    json_extract(event_data, '$.file') AS file,
                    json_extract(event_data, '$.line') AS line,
                    COUNT(*) AS count,
                    MAX(created_at) AS last_seen
                FROM telemetry_events
                WHERE site_key = ? AND event_type IN ('client_error', 'promise_rejection')
                GROUP BY message, file, line
                ORDER BY count DESC
                LIMIT 10;
            """, (site_key,))
            error_items = []
            for r in c.fetchall():
                error_items.append({
                    "message": r["message"] or "Error no especificado",
                    "file": r["file"] or "",
                    "line": r["line"] or 0,
                    "occurrences": r["count"],
                    "last_seen": r["last_seen"]
                })

            # 3. Cálculo de Friction Score (0-100)
            total_rage = sum(i["incidents"] for i in rage_items)
            total_err = sum(e["occurrences"] for e in error_items)
            deduction = min(total_rage * 10, 40) + min(total_err * 5, 40)
            score = max(100 - deduction, 10)

            status = "Excelente" if score >= 85 else ("Bueno" if score >= 70 else ("Fricción Moderada" if score >= 50 else "Crítico"))

            return {
                "friction_score": score,
                "status": status,
                "total_rage_clicks": total_rage,
                "total_client_errors": total_err,
                "rage_click_hotspots": rage_items,
                "client_errors_breakdown": error_items
            }


friction_analyzer = FrictionAnalyzer()
