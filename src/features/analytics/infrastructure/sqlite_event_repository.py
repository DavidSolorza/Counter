"""
Adaptador de persistencia SQLite para Eventos de Telemetría.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import List
from src.core.database.connection import DatabaseManager, db_manager
from src.features.analytics.domain.event_entity import TelemetryEvent
from src.features.analytics.domain.event_repository_interface import EventRepositoryInterface


class SqliteEventRepository(EventRepositoryInterface):
    """Implementación de persistencia para TelemetryEvent utilizando SQLite."""

    def __init__(self, manager: DatabaseManager = db_manager) -> None:
        self._manager = manager

    def save_batch(self, events: List[TelemetryEvent]) -> int:
        if not events:
            return 0

        query = """
            INSERT INTO telemetry_events (site_key, event_type, element_target, page_url)
            VALUES (?, ?, ?, ?);
        """
        payload_tuples = [
            (ev.site_key, ev.event_type, ev.element_target, ev.page_url)
            for ev in events
        ]

        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, payload_tuples)
            return cursor.rowcount

    def count_by_site_key(self, site_key: str) -> int:
        query = """
            SELECT COUNT(*) AS total
            FROM telemetry_events
            WHERE site_key = ?;
        """
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key,))
            row = cursor.fetchone()
            return int(row["total"]) if row else 0
