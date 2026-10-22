"""
Punto de entrada principal del servidor WolfAnalytics (Flask).
Gobernanza: Límite estricto < 150 líneas.
"""
from pathlib import Path
from flask import Flask, send_file, jsonify, Response
from flask_cors import CORS

from src.core.config.settings import settings
from src.core.database.connection import db_manager
from src.features.licensing.infrastructure.licensing_controller import licensing_bp
from src.features.analytics.infrastructure.analytics_controller import analytics_bp


def create_app() -> Flask:
    """Fábrica de la aplicación Flask."""
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Inicializar DDL de la base de datos de forma idempotente
    db_manager.initialize_schema()

    # Registro de módulos por Vertical Slicing
    app.register_blueprint(licensing_bp)
    app.register_blueprint(analytics_bp)

    @app.route("/", methods=["GET"])
    def index() -> tuple[Response, int]:
        return jsonify({
            "service": "WolfAnalytics API",
            "version": "1.1.0",
            "status": "online",
            "docs": "/docs/api/contracts.md",
            "test_ui": "/test"
        }), 200

    @app.route("/tracker.js", methods=["GET"])
    def serve_tracker() -> Response:
        tracker_file = Path(__file__).resolve().parent / "src" / "features" / "analytics" / "infrastructure" / "static" / "tracker.js"
        return send_file(tracker_file, mimetype="application/javascript")

    @app.route("/inyeccion.js", methods=["GET"])
    def serve_inyeccion() -> Response:
        inyeccion_file = Path(__file__).resolve().parent / "inyeccion.js"
        return send_file(inyeccion_file, mimetype="application/javascript")

    @app.route("/test", methods=["GET"])
    def serve_test_page() -> Response:
        test_file = Path(__file__).resolve().parent / "prueba.html"
        return send_file(test_file, mimetype="text/html")

    return app


if __name__ == "__main__":
    application = create_app()
    print(f"[WolfAnalytics] Servidor activo en http://{settings.HOST}:{settings.PORT}")
    print(f"[WolfAnalytics] Panel de prueba: http://{settings.HOST}:{settings.PORT}/test")
    print(f"[WolfAnalytics] SDK disponible: http://{settings.HOST}:{settings.PORT}/tracker.js")
    application.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
