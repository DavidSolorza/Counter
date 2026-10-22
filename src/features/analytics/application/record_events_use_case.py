"""
Caso de uso: Registro e Ingesta de Lotes de Telemetría.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import List, Dict, Any, Optional
from src.features.analytics.domain.event_entity import TelemetryEvent
from src.features.analytics.domain.event_repository_interface import EventRepositoryInterface
from src.features.licensing.domain.repository_interface import SiteRepositoryInterface
from src.core.errors.exceptions import (
    InvalidSiteKeyException,
    InactiveSiteException,
    InvalidTelemetryPayloadException
)


class RecordEventsUseCase:
    """Valida la autorización del sitio y almacena el lote de telemetría."""

    def __init__(
        self,
        site_repo: SiteRepositoryInterface,
        event_repo: EventRepositoryInterface
    ) -> None:
        self._site_repo = site_repo
        self._event_repo = event_repo

    def execute(self, site_key: Optional[str], raw_events: Optional[List[Dict[str, Any]]]) -> int:
        if not site_key or not site_key.strip():
            raise InvalidSiteKeyException("Clave de sitio ausente en la carga de eventos.")

        site = self._site_repo.get_by_site_key(site_key.strip())
        if not site:
            raise InvalidSiteKeyException("Sitio no autorizado para reportar telemetría.")

        if not site.can_track():
            raise InactiveSiteException("El sitio tiene la recolección desactivada.")

        if not raw_events or not isinstance(raw_events, list):
            raise InvalidTelemetryPayloadException("La lista de eventos no puede estar vacía.")

        event_entities: List[TelemetryEvent] = []
        for raw in raw_events:
            try:
                entity = TelemetryEvent(
                    site_key=site.site_key,
                    event_type=str(raw.get("type", "unknown")),
                    element_target=raw.get("target"),
                    page_url=str(raw.get("url", ""))
                )
                entity.validate()
                event_entities.append(entity)
            except ValueError as ex:
                continue

        if not event_entities:
            return 0

        return self._event_repo.save_batch(event_entities)
