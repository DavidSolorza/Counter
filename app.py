"""
app.py (Root Launcher)
Lanza el microservicio de analítica Flask en el puerto 5000.
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

FLASK_DIR = Path(__file__).resolve().parent / "back" / "flask-analytics"
if str(FLASK_DIR) not in sys.path:
    sys.path.insert(0, str(FLASK_DIR))

from app import create_app
from core.config import config

if __name__ == "__main__":
    app = create_app()
    print(f"[Counter] Servidor de Analítica activo en http://{config.HOST}:{config.PORT}/")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
