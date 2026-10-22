"""
back/flask-analytics/controllers/analytics_controller.py
Controlador REST para entregar datos analíticos procesados al Frontend.
Gobernanza: Límite estricto < 150 líneas.
"""
from flask import Blueprint, jsonify, Response

try:
    from analytics.analytics_engine import analytics_engine
    from analytics.funnel_processor import funnel_processor
    from analytics.friction_analyzer import friction_analyzer
    from analytics.visual_wireframe import visual_processor
    from analytics.session_metrics import session_calculator
except ImportError:
    from ..analytics.analytics_engine import analytics_engine
    from ..analytics.funnel_processor import funnel_processor
    from ..analytics.friction_analyzer import friction_analyzer
    from ..analytics.visual_wireframe import visual_processor
    from ..analytics.session_metrics import session_calculator

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/analytics")


@analytics_bp.route("/overview/<string:site_key>", methods=["GET"])
def get_overview(site_key: str) -> tuple[Response, int]:
    """Entrega el reporte analítico 360° consolidado para el Dashboard."""
    data = analytics_engine.get_overview(site_key)
    return jsonify({"success": True, "data": data}), 200


@analytics_bp.route("/funnel/<string:site_key>", methods=["GET"])
def get_funnel(site_key: str) -> tuple[Response, int]:
    """Entrega el embudo de conversión y tasas de abandono."""
    funnel = funnel_processor.calculate_funnel(site_key)
    return jsonify({"success": True, "site_key": site_key, "funnel": funnel}), 200


@analytics_bp.route("/friction/<string:site_key>", methods=["GET"])
def get_friction(site_key: str) -> tuple[Response, int]:
    """Entrega el reporte de puntos de fricción, rage clicks y errores de cliente."""
    report = friction_analyzer.get_friction_report(site_key)
    return jsonify({"success": True, "site_key": site_key, "friction": report}), 200


@analytics_bp.route("/visuals/<string:site_key>", methods=["GET"])
def get_visuals(site_key: str) -> tuple[Response, int]:
    """Entrega la galería de componentes visuales interactuados con estilos CSS."""
    components = visual_processor.get_components_gallery(site_key)
    return jsonify({"success": True, "site_key": site_key, "components": components}), 200


@analytics_bp.route("/sessions/<string:site_key>", methods=["GET"])
def get_sessions(site_key: str) -> tuple[Response, int]:
    """Entrega KPIs de sesión, tasa de rebote y permanencia."""
    kpis = session_calculator.get_session_kpis(site_key)
    return jsonify({"success": True, "site_key": site_key, "kpis": kpis}), 200
