"""
back/flask-analytics/controllers/telemetry_controller.py
Controlador de ingesta masiva y consultas analíticas en Flask.
Gobernanza: Límite estricto < 150 líneas.
"""
import json
from flask import Blueprint, request, jsonify, Response

try:
    from database.repositories.event_repository import EventRepository
    from enrichment.user_agent_parser import ua_parser
    from enrichment.geo_ip_enricher import geo_enricher
    from core.rate_limiter import rate_limiter
    from analytics.analytics_engine import analytics_engine
except ImportError:
    from ..database.repositories.event_repository import EventRepository
    from ..enrichment.user_agent_parser import ua_parser
    from ..enrichment.geo_ip_enricher import geo_enricher
    from ..core.rate_limiter import rate_limiter
    from ..analytics.analytics_engine import analytics_engine

telemetry_bp = Blueprint("telemetry", __name__)
_event_repo = EventRepository()


def _get_payload() -> dict:
    if request.is_json:
        return request.get_json(silent=True) or {}
    if request.data:
        try:
            return json.loads(request.data.decode("utf-8"))
        except Exception:
            return {}
    return {}


@telemetry_bp.route("/health", methods=["GET"])
def health_check() -> tuple[Response, int]:
    return jsonify({
        "status": "UP",
        "service": "Counter Analytics Microservice",
        "port": 5000,
        "database": "analytics.db"
    }), 200


@telemetry_bp.route("/api/v1/telemetry/collect", methods=["POST"])
@telemetry_bp.route("/api/v1/telemetry", methods=["POST"])
def collect_telemetry() -> tuple[Response, int]:
    client_ip = geo_enricher.extract_ip(dict(request.headers), request.remote_addr)

    if not rate_limiter.is_allowed(client_ip):
        return jsonify({"success": False, "error": "Límite de tasa excedido."}), 429

    payload = _get_payload()
    site_key = payload.get("site_key")
    raw_events = payload.get("events")

    if not site_key:
        return jsonify({"success": False, "error": "Site Key ausente."}), 400

    if not raw_events or not isinstance(raw_events, list):
        return jsonify({"success": False, "error": "Lista de eventos vacía o inválida."}), 400

    ua_meta = ua_parser.parse(request.headers.get("User-Agent", ""))
    geo_meta = geo_enricher.enrich(client_ip)

    for ev in raw_events:
        if "event_data" not in ev or not isinstance(ev["event_data"], dict):
            ev["event_data"] = {}
        ev["event_data"]["_client"] = ua_meta
        ev["event_data"]["_network"] = geo_meta

    stored = _event_repo.save_batch(site_key, raw_events)
    return jsonify({"success": True, "stored": stored}), 200


@telemetry_bp.route("/api/v1/analytics/summary/<string:site_key>", methods=["GET"])
def get_analytics_summary(site_key: str) -> tuple[Response, int]:
    summary = analytics_engine.get_summary(site_key)
    return jsonify(summary), 200


@telemetry_bp.route("/api/v1/events/<string:site_key>", methods=["GET"])
def get_events(site_key: str) -> tuple[Response, int]:
    limit = int(request.args.get("limit", 10))
    events = _event_repo.get_recent(site_key, limit=limit)
    return jsonify({"site_key": site_key, "events": events}), 200
