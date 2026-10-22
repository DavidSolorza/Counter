"""
back/app.py
Punto de entrada de la API REST del backend Counter.
Gobernanza: Límite estricto < 150 líneas.
"""
from pathlib import Path
from flask import Flask, send_file, jsonify, Response
from flask_cors import CORS
try:
    from back.logic.database.connection import db
    from back.logic.core.config import config
    from back.logic.controllers.licensing_controller import licensing_bp
    from back.logic.controllers.telemetry_controller import telemetry_bp
except ImportError:
    from database.connection import db
    from backend.core.config import config
    from backend.controllers.licensing_controller import licensing_bp
    from backend.controllers.telemetry_controller import telemetry_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Inicializar DDL en SQLite
    db.initialize_schema()

    # Registro de Blueprints REST
    app.register_blueprint(licensing_bp)
    app.register_blueprint(telemetry_bp)

    @app.route("/", methods=["GET"])
    def index() -> tuple[Response, int]:
        return jsonify({
            "service": "Counter Analytics API",
            "status": "online",
            "version": "3.1.0",
            "sdk_url": "/counter.js",
            "download_url": "/download/counter.js"
        }), 200

    @app.route("/counter.js", methods=["GET"])
    @app.route("/sdk/counter.js", methods=["GET"])
    @app.route("/tracker.js", methods=["GET"])
    def serve_sdk() -> Response:
        sdk_file = Path(__file__).resolve().parent / "library" / "tracker.js"
        return send_file(sdk_file, mimetype="application/javascript")

    @app.route("/download/counter.js", methods=["GET"])
    def download_sdk() -> Response:
        sdk_file = Path(__file__).resolve().parent / "library" / "tracker.js"
        return send_file(sdk_file, as_attachment=True, download_name="counter.js")

    @app.route("/test", methods=["GET"])
    def serve_test() -> Response:
        test_file = Path(__file__).resolve().parent.parent / "prueba.html"
        return send_file(test_file, mimetype="text/html")

    return app


if __name__ == "__main__":
    app_instance = create_app()
    print(f"[Counter] Backend activo en http://{config.HOST}:{config.PORT}/")
    print(f"[Counter] Librería distribuible en http://{config.HOST}:{config.PORT}/counter.js")
    app_instance.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
