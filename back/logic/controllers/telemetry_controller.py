"""
back/logic/controllers/telemetry_controller.py
Controlador de ingesta de telemetría y consultas analíticas agregadas.
Gobernanza: Límite estricto < 150 líneas.
"""
import json
from flask import Blueprint, request, jsonify, Response
try:
    from back.logic.database.repositories.site_repository import SiteRepository
    from back.logic.database.repositories.event_repository import EventRepository
    from back.logic.enrichment.user_agent_parser import ua_parser
    from back.logic.enrichment.geo_ip_enricher import geo_enricher
    from back.logic.core.rate_limiter import rate_limiter
    from back.logic.analytics.analytics_engine import analytics_engine
except ImportError:
    from database.repositories.site_repository import SiteRepository
    from database.repositories.event_repository import EventRepository
    from backend.enrichment.user_agent_parser import ua_parser
    from backend.enrichment.geo_ip_enricher import geo_enricher
    from backend.core.rate_limiter import rate_limiter
    from backend.analytics.analytics_engine import analytics_engine

telemetry_bp = Blueprint("telemetry", __name__, url_prefix="/api/v1")
_site_repo = SiteRepository()
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


@telemetry_bp.route("/telemetry", methods=["POST"])
def receive_telemetry() -> tuple[Response, int]:
    client_ip = geo_enricher.extract_ip(dict(request.headers), request.remote_addr)

    if not rate_limiter.is_allowed(client_ip):
        return jsonify({"success": False, "error": "Límite de tasa excedido. Intenta más tarde."}), 429

    payload = _get_payload()
    site_key = payload.get("site_key")
    raw_events = payload.get("events")

    if not site_key or not _site_repo.find_by_key(site_key):
        return jsonify({"success": False, "error": "Site Key inválida o no autorizada."}), 403

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


@telemetry_bp.route("/analytics/summary/<string:site_key>", methods=["GET"])
def get_analytics_summary(site_key: str) -> tuple[Response, int]:
    summary = analytics_engine.get_summary(site_key)
    return jsonify(summary), 200


@telemetry_bp.route("/stats/<string:site_key>", methods=["GET"])
def get_stats(site_key: str) -> tuple[Response, int]:
    total = _event_repo.count_by_site(site_key)
    return jsonify({"site_key": site_key, "total_events": total}), 200


@telemetry_bp.route("/events/<string:site_key>", methods=["GET"])
def get_events(site_key: str) -> tuple[Response, int]:
    limit = int(request.args.get("limit", 10))
    events = _event_repo.get_recent(site_key, limit=limit)
    return jsonify({"site_key": site_key, "events": events}), 200
