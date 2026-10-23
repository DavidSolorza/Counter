"""
back/flask-analytics/database/repositories/event_repository.py
Persistencia y consulta de telemetría en analytics.db.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import List, Dict, Any
import json

try:
    from database.connection import db, AnalyticsDatabaseManager
except ImportError:
    from ..connection import db, AnalyticsDatabaseManager


class EventRepository:
    def __init__(self, manager: AnalyticsDatabaseManager = db) -> None:
        self._manager = manager

    def save_batch(self, site_key: str, events: List[Dict[str, Any]]) -> int:
        if not events:
            return 0
        query = """
            INSERT INTO telemetry_events (site_key, session_id, event_type, page_url, element_selector, event_data)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb);
        """
        records = []
        for ev in events:
            ev_data = ev.get("event_data", {})
            if not isinstance(ev_data, dict):
                ev_data = {}
            sid = ev.get("session_id") or ev_data.get("_sid")
            el_sel = ev.get("element_selector") or ev_data.get("element")
            records.append((
                site_key,
                str(sid) if sid else None,
                str(ev.get("event_type") or ev.get("type", "unknown")),
                str(ev.get("page_url") or ev.get("url", "")),
                str(el_sel)[:255] if el_sel else None,
                json.dumps(ev_data, ensure_ascii=False)
            ))
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, records)
            return cursor.rowcount

    def count_by_site(self, site_key: str) -> int:
        query = "SELECT COUNT(*) AS total FROM telemetry_events WHERE site_key = %s;"
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key,))
            row = cursor.fetchone()
            return int(row["total"]) if row else 0

    def get_recent(self, site_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT id, site_key, event_type, page_url, event_data, created_at
            FROM telemetry_events
            WHERE site_key = %s
            ORDER BY id DESC
            LIMIT %s;
        """
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key, limit))
            output = []
            for r in cursor.fetchall():
                raw_data = r["event_data"]
                if isinstance(raw_data, dict):
                    pdata = raw_data
                else:
                    try:
                        pdata = json.loads(raw_data) if raw_data else {}
                    except Exception:
                        pdata = {}
                created_val = r["created_at"]
                created_str = created_val.isoformat() if hasattr(created_val, "isoformat") else str(created_val)
                output.append({
                    "id": r["id"],
                    "site_key": r["site_key"],
                    "event_type": r["event_type"],
                    "page_url": r["page_url"],
                    "event_data": pdata,
                    "created_at": created_str
                })
            return output
