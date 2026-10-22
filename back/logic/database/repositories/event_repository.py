"""
back/logic/database/repositories/event_repository.py
Persistencia y consulta de eventos de telemetría con payloads JSON.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import List, Dict, Any
import json
try:
    from back.logic.database.connection import db, DatabaseManager
except ImportError:
    from database.connection import db, DatabaseManager


class EventRepository:
    """Manejo de persistencia de telemetría con columna JSON."""

    def __init__(self, manager: DatabaseManager = db) -> None:
        self._manager = manager

    def save_batch(self, site_key: str, events: List[Dict[str, Any]]) -> int:
        if not events:
            return 0

        query = """
            INSERT INTO telemetry_events (site_key, event_type, page_url, event_data)
            VALUES (?, ?, ?, ?);
        """
        records = [
            (
                site_key,
                str(ev.get("event_type") or ev.get("type", "unknown")),
                str(ev.get("page_url") or ev.get("url", "")),
                json.dumps(ev.get("event_data", {}), ensure_ascii=False)
            )
            for ev in events
        ]

        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, records)
            return cursor.rowcount

    def count_by_site(self, site_key: str) -> int:
        query = "SELECT COUNT(*) AS total FROM telemetry_events WHERE site_key = ?;"
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key,))
            row = cursor.fetchone()
            return int(row["total"]) if row else 0

    def get_recent(self, site_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT id, site_key, event_type, page_url, event_data, created_at
            FROM telemetry_events
            WHERE site_key = ?
            ORDER BY id DESC
            LIMIT ?;
        """
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key, limit))
            rows = cursor.fetchall()
            output = []
            for r in rows:
                try:
                    pdata = json.loads(r["event_data"]) if r["event_data"] else {}
                except Exception:
                    pdata = {}
                output.append({
                    "id": r["id"],
                    "site_key": r["site_key"],
                    "event_type": r["event_type"],
                    "page_url": r["page_url"],
                    "event_data": pdata,
                    "created_at": r["created_at"]
                })
            return output

    def find_recent_by_site(self, site_key: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.get_recent(site_key, limit)
