"""
backend/app.py
Punto de entrada de la aplicación Flask en backend/.
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

    # Inicializar esquemas DDL en SQLite
    db.initialize_schema()

    # Registro de Blueprints
    app.register_blueprint(licensing_bp)
    app.register_blueprint(telemetry_bp)

    @app.route("/", methods=["GET"])
    def index() -> tuple[Response, int]:
        return jsonify({
            "service": "WolfAnalytics Enterprise API",
            "version": "2.1.0",
            "status": "online",
            "endpoints": {
                "handshake": "/api/v1/verify",
                "telemetry": "/api/v1/telemetry",
                "stats": "/api/v1/stats/<site_key>",
                "events": "/api/v1/events/<site_key>",
                "dashboard": "/dashboard"
            },
            "sdk_url": "/sdk/tracker.js"
        }), 200

    @app.route("/dashboard", methods=["GET"])
    def serve_dashboard() -> Response:
        dash_file = Path(__file__).resolve().parent / "dashboard.html"
        return send_file(dash_file, mimetype="text/html")

    @app.route("/sdk/tracker.js", methods=["GET"])
    @app.route("/tracker.js", methods=["GET"])
    def serve_sdk() -> Response:
        sdk_file = config.SDK_DIR / "tracker.js"
        return send_file(sdk_file, mimetype="application/javascript")

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
    print(f"[WolfAnalytics] Dashboard en vivo: http://{config.HOST}:{config.PORT}/dashboard")
    print(f"[WolfAnalytics] SDK empresarial: http://{config.HOST}:{config.PORT}/sdk/tracker.js")
    app_instance.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
