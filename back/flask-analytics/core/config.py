"""
back/flask-analytics/core/config.py
Configuración del microservicio de analítica Counter.
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass
from pathlib import Path
import os

FLASK_DIR = Path(__file__).resolve().parent.parent
DB_FILE = FLASK_DIR / "analytics.db"

@dataclass(frozen=True)
class AnalyticsConfig:
    HOST: str = os.getenv("ANALYTICS_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("ANALYTICS_PORT", "5000"))
    DEBUG: bool = os.getenv("ANALYTICS_DEBUG", "True").lower() == "true"
    DB_PATH: Path = DB_FILE

config = AnalyticsConfig()
