"""
backend/app.py
Punto de entrada de la plataforma Counter en backend/.
Gobernanza: Límite estricto < 150 líneas.
"""
from pathlib import Path
from flask import Flask, send_file, jsonify, Response
from flask_cors import CORS
from database.connection import db
from backend.core.config import config
from backend.controllers.licensing_controller import licensing_bp
from backend.controllers.telemetry_controller import telemetry_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Inicializar DDL en SQLite
    db.initialize_schema()

    # Registro de Blueprints
    app.register_blueprint(licensing_bp)
    app.register_blueprint(telemetry_bp)

    @app.route("/", methods=["GET"])
    def index() -> Response:
        dash_file = Path(__file__).resolve().parent / "dashboard.html"
        return send_file(dash_file, mimetype="text/html")

    @app.route("/dashboard", methods=["GET"])
    def serve_dashboard() -> Response:
        dash_file = Path(__file__).resolve().parent / "dashboard.html"
        return send_file(dash_file, mimetype="text/html")

    @app.route("/sdk/tracker.js", methods=["GET"])
    @app.route("/tracker.js", methods=["GET"])
    @app.route("/sdk/counter.js", methods=["GET"])
    @app.route("/counter.js", methods=["GET"])
    def serve_sdk() -> Response:
        sdk_file = config.SDK_DIR / "tracker.js"
        return send_file(sdk_file, mimetype="application/javascript")

    @app.route("/download/counter.js", methods=["GET"])
    def download_sdk() -> Response:
        sdk_file = config.SDK_DIR / "tracker.js"
        return send_file(sdk_file, as_attachment=True, download_name="counter.js")

    @app.route("/inyeccion.js", methods=["GET"])
    def serve_microfooter() -> Response:
        f = Path(config.SDK_DIR).parent / "inyeccion.js"
        return send_file(f, mimetype="application/javascript")

    @app.route("/test", methods=["GET"])
    def serve_test() -> Response:
        return send_file(config.TEST_HTML, mimetype="text/html")

    return app


if __name__ == "__main__":
    app_instance = create_app()
    print(f"[Counter] Portal oficial activo en http://{config.HOST}:{config.PORT}/")
    print(f"[Counter] SDK descargable en: http://{config.HOST}:{config.PORT}/download/counter.js")
    app_instance.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
