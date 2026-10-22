"""
app.py (Root Launcher)
Delega la ejecución al entrypoint modular en back/app.py.
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

# Añadir raíz al sys.path para imports absolutos
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from back.app import create_app
from back.logic.core.config import config

if __name__ == "__main__":
    app = create_app()
    print(f"[Counter] Servidor iniciado desde back/app.py en http://{config.HOST}:{config.PORT}/")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
