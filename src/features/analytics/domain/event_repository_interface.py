"""
Contrato de interfaz para el repositorio de Eventos de Telemetría.
Gobernanza: Límite estricto < 150 líneas.
"""
from abc import ABC, abstractmethod
from typing import List
from src.features.analytics.domain.event_entity import TelemetryEvent


class EventRepositoryInterface(ABC):
    """Contrato abstracto para la persistencia masiva de eventos."""

    @abstractmethod
    def save_batch(self, events: List[TelemetryEvent]) -> int:
        """Persiste una colección de eventos en una única transacción atómica."""
        pass

    @abstractmethod
    def count_by_site_key(self, site_key: str) -> int:
        """Retorna el número acumulado de eventos registrados para un sitio."""
        pass
