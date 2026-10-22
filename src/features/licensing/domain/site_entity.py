"""
Entidad de dominio: Site (Licencia y Sitio Autorizado).
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Site:
    """Representa una entidad de sitio registrado en el sistema."""
    site_key: str
    domain: str
    owner_email: str
    is_active: bool
    id: Optional[int] = None
    created_at: Optional[str] = None

    def can_track(self) -> bool:
        """Determina si el sitio tiene autorización activa para recolectar analítica."""
        return bool(self.is_active)

    def is_matching_domain(self, target_domain: Optional[str]) -> bool:
        """Valida si un dominio coincide o si está en entorno local."""
        if not target_domain:
            return True
        if self.domain in ("localhost", "127.0.0.1", "*"):
            return True
        return target_domain.lower() == self.domain.lower()
