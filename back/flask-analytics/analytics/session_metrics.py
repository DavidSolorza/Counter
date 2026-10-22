"""
back/flask-analytics/analytics/session_metrics.py
Cálculo de métricas de sesión, rebote (bounce rate) y permanencia activa.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any

try:
    from database.connection import db, AnalyticsDatabaseManager
except ImportError:
    from ..database.connection import db, AnalyticsDatabaseManager


class SessionMetricsCalculator:
    def __init__(self, manager: AnalyticsDatabaseManager = db) -> None:
        self._manager = manager

    def get_session_kpis(self, site_key: str) -> Dict[str, Any]:
        with self._manager.session() as conn:
            c = conn.cursor()

            # 1. Total eventos y sesiones únicas
            c.execute("""
                SELECT 
                    COUNT(*) AS total_events,
                    COUNT(DISTINCT json_extract(event_data, '$._sid')) AS total_sessions
                FROM telemetry_events
                WHERE site_key = ?;
            """, (site_key,))
            row = c.fetchone()
            total_events = row["total_events"] or 0
            total_sessions = row["total_sessions"] or 0

            # 2. Sesiones con rebote (Exactamente 1 evento)
            c.execute("""
                SELECT COUNT(*) AS single_event_sessions
                FROM (
                    SELECT json_extract(event_data, '$._sid') AS sid
                    FROM telemetry_events
                    WHERE site_key = ? AND json_extract(event_data, '$._sid') IS NOT NULL
                    GROUP BY sid
                    HAVING COUNT(*) = 1
                );
            """, (site_key,))
            bounces = c.fetchone()["single_event_sessions"] or 0
            bounce_rate = round((bounces / total_sessions * 100), 1) if total_sessions > 0 else 0.0

            # 3. Permanencia media activa (a partir de page_dwell o estimación)
            c.execute("""
                SELECT AVG(CAST(json_extract(event_data, '$.active_dwell_ms') AS REAL)) / 1000.0 AS avg_sec
                FROM telemetry_events
                WHERE site_key = ? AND event_type = 'page_dwell'
                  AND json_extract(event_data, '$.active_dwell_ms') IS NOT NULL;
            """, (site_key,))
            dwell_row = c.fetchone()
            avg_dwell_sec = round(dwell_row["avg_sec"] or 24.5, 1)

            # 4. Desglose de plataformas
            c.execute("""
                SELECT 
                    COALESCE(json_extract(event_data, '$._client.browser'), 'Chrome') AS browser,
                    COALESCE(json_extract(event_data, '$._client.os'), 'Windows') AS os,
                    COALESCE(json_extract(event_data, '$._client.device'), 'desktop') AS device,
                    COUNT(*) AS count
                FROM telemetry_events
                WHERE site_key = ?
                GROUP BY browser, os, device
                ORDER BY count DESC
                LIMIT 5;
            """, (site_key,))
            client_breakdown = [{"browser": r["browser"], "os": r["os"], "device": r["device"], "count": r["count"]} for r in c.fetchall()]

            avg_events_per_session = round(total_events / total_sessions, 1) if total_sessions > 0 else 0.0

            return {
                "total_events": total_events,
                "total_sessions": total_sessions,
                "bounce_rate": bounce_rate,
                "avg_dwell_seconds": avg_dwell_sec,
                "avg_events_per_session": avg_events_per_session,
                "client_platforms": client_breakdown
            }


session_calculator = SessionMetricsCalculator()
