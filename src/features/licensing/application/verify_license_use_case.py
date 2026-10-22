"""
Caso de uso: Verificación y Handshake de Licencia.
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass
from typing import Optional
from src.features.licensing.domain.repository_interface import SiteRepositoryInterface
from src.core.errors.exceptions import InvalidSiteKeyException, InactiveSiteException


@dataclass(frozen=True)
class VerificationResult:
    valid: bool
    message: str
    domain: str


class VerifyLicenseUseCase:
    """Caso de uso para autenticar una Site Key y verificar su vigencia."""

    def __init__(self, repository: SiteRepositoryInterface) -> None:
        self._repository = repository

    def execute(self, site_key: Optional[str], client_domain: Optional[str] = None) -> VerificationResult:
        if not site_key or not site_key.strip():
            raise InvalidSiteKeyException("Site Key ausente o inválida.")

        site = self._repository.get_by_site_key(site_key.strip())
        if not site:
            raise InvalidSiteKeyException("La Site Key no se encuentra registrada.")

        if not site.can_track():
            raise InactiveSiteException("El sitio tiene el interruptor de analítica desactivado.")

        if client_domain and not site.is_matching_domain(client_domain):
            raise InactiveSiteException(f"Dominio no autorizado para esta llave: {client_domain}")

        return VerificationResult(
            valid=True,
            message="Licencia activa. SDK desbloqueado.",
            domain=site.domain
        )
