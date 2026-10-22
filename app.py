"""
app.py
Punto de acceso raíz delegando a backend.app.
Gobernanza: Límite estricto < 150 líneas.
"""
from backend.app import create_app
from backend.core.config import config

application = create_app()

if __name__ == "__main__":
    print(f"[WolfAnalytics] Iniciando servicio en http://{config.HOST}:{config.PORT}")
    application.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
