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
    HOST: str = os.getenv("ANALYTICS_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", os.getenv("ANALYTICS_PORT", "5000")))
    DEBUG: bool = os.getenv("ANALYTICS_DEBUG", "False").lower() == "true"
    DB_PATH: Path = DB_FILE
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('PG_USER', 'mi_usuario')}:{os.getenv('PG_PASSWORD', 'mi_password')}@{os.getenv('PG_HOST', 'mi-servidor-db')}:{os.getenv('PG_PORT', '5432')}/{os.getenv('PG_DB', 'counter_db')}"
    )

config = AnalyticsConfig()
