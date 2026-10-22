"""
backend/core/config.py
Configuración centralizada del backend WolfAnalytics.
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dataclass(frozen=True)
class BackendConfig:
    HOST: str = os.getenv("WOLF_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("WOLF_PORT", "5000"))
    DEBUG: bool = os.getenv("WOLF_DEBUG", "True").lower() == "true"
    DEFAULT_KEY: str = "wk_test_12345"
    SDK_DIR: Path = BASE_DIR / "sdk"
    TEST_HTML: Path = BASE_DIR / "prueba.html"

config = BackendConfig()
