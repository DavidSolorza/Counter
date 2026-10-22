"""
Adaptador de persistencia SQLite para Eventos de Telemetría con soporte JSON.
Gobernanza: Límite estricto < 150 líneas.
"""
import json
from typing import List, Dict, Any
from src.core.database.connection import DatabaseManager, db_manager
from src.features.analytics.domain.event_entity import TelemetryEvent
from src.features.analytics.domain.event_repository_interface import EventRepositoryInterface


class SqliteEventRepository(EventRepositoryInterface):
    """Implementación de persistencia para TelemetryEvent en SQLite con columna JSON."""

    def __init__(self, manager: DatabaseManager = db_manager) -> None:
        self._manager = manager

    def save_batch(self, events: List[TelemetryEvent]) -> int:
        if not events:
            return 0

        query = """
            INSERT INTO telemetry_events (site_key, event_type, page_url, event_data)
            VALUES (?, ?, ?, ?);
        """
        payload_tuples = [
            (
                ev.site_key,
                ev.event_type,
                ev.page_url,
                json.dumps(ev.event_data if isinstance(ev.event_data, dict) else {}, ensure_ascii=False)
            )
            for ev in events
        ]

        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, payload_tuples)
            return cursor.rowcount

    def count_by_site_key(self, site_key: str) -> int:
        query = "SELECT COUNT(*) AS total FROM telemetry_events WHERE site_key = ?;"
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key,))
            row = cursor.fetchone()
            return int(row["total"]) if row else 0

    def get_recent_by_site_key(self, site_key: str, limit: int = 10) -> List[Dict[str, Any]]:
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
            results = []
            for r in rows:
                try:
                    parsed_data = json.loads(r["event_data"]) if r["event_data"] else {}
                except Exception:
                    parsed_data = {}
                results.append({
                    "id": r["id"],
                    "site_key": r["site_key"],
                    "event_type": r["event_type"],
                    "page_url": r["page_url"],
                    "event_data": parsed_data,
                    "created_at": r["created_at"]
                })
            return results
