"""
Adaptador de infraestructura SQLite para el repositorio de Sitios.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Optional
from src.core.database.connection import DatabaseManager, db_manager
from src.features.licensing.domain.site_entity import Site
from src.features.licensing.domain.repository_interface import SiteRepositoryInterface


class SqliteSiteRepository(SiteRepositoryInterface):
    """Implementación de persistencia para Sitios utilizando SQLite."""

    def __init__(self, manager: DatabaseManager = db_manager) -> None:
        self._manager = manager

    def get_by_site_key(self, site_key: str) -> Optional[Site]:
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
            return Site(
                id=row["id"],
                site_key=row["site_key"],
                domain=row["domain"],
                owner_email=row["owner_email"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"]
            )

    def save(self, site: Site) -> Site:
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
            cursor.execute(query, (site.site_key, site.domain, site.owner_email, int(site.is_active)))
            if not site.id:
                site.id = cursor.lastrowid
        return site
