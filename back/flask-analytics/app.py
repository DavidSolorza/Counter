"""
back/flask-analytics/app.py
Punto de entrada del microservicio de analítica Counter (Puerto 5000).
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

FLASK_DIR = Path(__file__).resolve().parent
if str(FLASK_DIR) not in sys.path:
    sys.path.insert(0, str(FLASK_DIR))

from flask import Flask, send_file, jsonify, Response
from flask_cors import CORS

try:
    from database.connection import db
    from core.config import config
    from controllers.telemetry_controller import telemetry_bp
except ImportError:
    from .database.connection import db
    from .core.config import config
    from .controllers.telemetry_controller import telemetry_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Inicializar DDL en analytics.db
    db.initialize_schema()

    # Registro de rutas de analítica
    app.register_blueprint(telemetry_bp)

    @app.route("/", methods=["GET"])
    def root() -> tuple[Response, int]:
        return jsonify({
            "service": "Counter Analytics Microservice",
            "status": "UP",
            "port": 5000,
            "database": "analytics.db",
            "telemetry_endpoint": "/api/v1/telemetry/collect"
        }), 200

    @app.route("/counter.js", methods=["GET"])
    @app.route("/tracker.js", methods=["GET"])
    def serve_sdk() -> Response:
        sdk_path = Path(__file__).resolve().parent.parent / "library" / "tracker.js"
        return send_file(sdk_path, mimetype="application/javascript")

    @app.route("/download/counter.js", methods=["GET"])
    def download_sdk() -> Response:
        sdk_path = Path(__file__).resolve().parent.parent / "library" / "tracker.js"
        return send_file(sdk_path, as_attachment=True, download_name="counter.js")

    @app.route("/test", methods=["GET"])
    def serve_test() -> Response:
        test_file = Path(__file__).resolve().parent.parent.parent / "prueba.html"
        return send_file(test_file, mimetype="text/html")

    return app


if __name__ == "__main__":
    app_instance = create_app()
    print(f"[Counter] Microservicio de Analítica activo en http://{config.HOST}:{config.PORT}/")
    app_instance.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
