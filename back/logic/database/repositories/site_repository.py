"""
back/logic/database/repositories/site_repository.py
Acceso a datos de Sitios y Licencias en SQLite.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Optional, Dict, Any
try:
    from back.logic.database.connection import db, DatabaseManager
except ImportError:
    from database.connection import db, DatabaseManager


class SiteRepository:
    """Manejo de persistencia para sitios y verificación de licencias."""

    def __init__(self, manager: DatabaseManager = db) -> None:
        self._manager = manager

    def find_by_key(self, site_key: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT id, site_key, domain, owner_email, is_active, created_at
            FROM sites
            WHERE site_key = ?
            LIMIT 1;
        """
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key,))
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)

    def create_site(self, site_key: str, domain: str, email: str) -> bool:
        query = """
            INSERT OR IGNORE INTO sites (site_key, domain, owner_email)
            VALUES (?, ?, ?);
        """
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key, domain, email))
            return cursor.rowcount > 0
