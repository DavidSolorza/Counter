"""
Configuración centralizada del sistema WolfAnalytics.
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

@dataclass(frozen=True)
class Settings:
    DB_NAME: str = os.getenv("WOLF_DB_NAME", "local_analytics.db")
    DB_PATH: Path = BASE_DIR / DB_NAME
    SCHEMA_PATH: Path = BASE_DIR / "docs" / "database" / "001_initial_schema.sql"
    HOST: str = os.getenv("WOLF_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("WOLF_PORT", "5000"))
    DEBUG: bool = os.getenv("WOLF_DEBUG", "True").lower() == "true"
    DEFAULT_SITE_KEY: str = "wk_test_12345"

settings = Settings()
