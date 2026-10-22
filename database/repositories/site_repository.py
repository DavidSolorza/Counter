"""
database/repositories/site_repository.py
Acceso a datos de Sitios y Licencias en SQLite.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Optional, Dict, Any
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
            return {
                "id": row["id"],
                "site_key": row["site_key"],
                "domain": row["domain"],
                "owner_email": row["owner_email"],
                "is_active": bool(row["is_active"]),
                "created_at": row["created_at"]
            }

    def upsert(self, site_key: str, domain: str, email: str, is_active: bool = True) -> int:
        query = """
            INSERT INTO sites (site_key, domain, owner_email, is_active)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(site_key) DO UPDATE SET
                domain = excluded.domain,
                owner_email = excluded.owner_email,
                is_active = excluded.is_active;
        """
        with self._manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (site_key, domain, email, int(is_active)))
            return cursor.lastrowid
