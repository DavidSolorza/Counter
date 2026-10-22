"""
Entidad de dominio: TelemetryEvent (Evento de Telemetría).
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemetryEvent:
    """Representa una acción o medición capturada por el SDK cliente."""
    site_key: str
    event_type: str
    element_target: Optional[str]
    page_url: str
    id: Optional[int] = None
    created_at: Optional[str] = None

    def validate(self) -> None:
        """Verifica la integridad de los datos mínimos requeridos."""
        if not self.site_key or not self.site_key.strip():
            raise ValueError("El site_key es obligatorio.")
        if not self.event_type or not self.event_type.strip():
            raise ValueError("El event_type es obligatorio.")
        if not self.page_url or not self.page_url.strip():
            raise ValueError("El page_url es obligatorio.")
