"""
Entidad de dominio: TelemetryEvent (Evento de Telemetría Híbrido).
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class TelemetryEvent:
    """Representa una acción o medición con carga útil variable JSON."""
    site_key: str
    event_type: str
    page_url: str
    event_data: Dict[str, Any] = field(default_factory=dict)
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
        if not isinstance(self.event_data, dict):
            raise ValueError("El event_data debe ser un diccionario.")
