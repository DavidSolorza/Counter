"""
Contrato de interfaz para el repositorio de Sitios.
Gobernanza: Límite estricto < 150 líneas.
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.features.licensing.domain.site_entity import Site


class SiteRepositoryInterface(ABC):
    """Contrato abstracto para la persistencia y recuperación de sitios."""

    @abstractmethod
    def get_by_site_key(self, site_key: str) -> Optional[Site]:
        """Obtiene un sitio por su clave de activación única."""
        pass

    @abstractmethod
    def save(self, site: Site) -> Site:
        """Persiste o actualiza un sitio en el almacenamiento."""
        pass
