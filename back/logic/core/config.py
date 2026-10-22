"""
back/logic/core/config.py
Configuración centralizada del backend Counter.
Gobernanza: Límite estricto < 150 líneas.
"""
from dataclasses import dataclass
from pathlib import Path
import os

BACK_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BACK_DIR.parent

@dataclass(frozen=True)
class BackendConfig:
    HOST: str = os.getenv("COUNTER_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("COUNTER_PORT", "5000"))
    DEBUG: bool = os.getenv("COUNTER_DEBUG", "True").lower() == "true"
    DEFAULT_KEY: str = "wk_test_12345"
    BACK_DIR: Path = BACK_DIR
    LIBRARY_DIR: Path = BACK_DIR / "library"
    SDK_FILE: Path = BACK_DIR / "library" / "tracker.js"
    TEST_HTML: Path = REPO_ROOT / "prueba.html"

config = BackendConfig()
