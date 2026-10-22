"""
Controlador HTTP Flask para la ingesta de telemetría y consulta de estadísticas.
Gobernanza: Límite estricto < 150 líneas.
"""
import json
from flask import Blueprint, request, jsonify, Response
from src.features.licensing.infrastructure.sqlite_site_repository import SqliteSiteRepository
from src.features.analytics.infrastructure.sqlite_event_repository import SqliteEventRepository
from src.features.analytics.application.record_events_use_case import RecordEventsUseCase
from src.core.errors.exceptions import AppException

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1")
_site_repo = SqliteSiteRepository()
_event_repo = SqliteEventRepository()
_record_use_case = RecordEventsUseCase(_site_repo, _event_repo)


def _extract_payload() -> dict:
    """Extrae el payload compatible con JSON o sendBeacon."""
    if request.is_json:
        return request.get_json(silent=True) or {}
    if request.data:
        try:
            return json.loads(request.data.decode("utf-8"))
        except Exception:
            return {}
    return {}


@analytics_bp.route("/telemetry", methods=["POST"])
def receive_telemetry() -> tuple[Response, int]:
    """Endpoint de ingesta de eventos de analítica."""
    payload = _extract_payload()
    site_key = payload.get("site_key")
    events = payload.get("events")

    try:
        stored_count = _record_use_case.execute(site_key, events)
        return jsonify({"success": True, "stored": stored_count}), 200
    except AppException as ex:
        return jsonify({"success": False, "error": ex.message}), ex.status_code
    except Exception:
        return jsonify({"success": False, "error": "Error interno al procesar telemetría."}), 500


@analytics_bp.route("/stats/<string:site_key>", methods=["GET"])
def get_site_stats(site_key: str) -> tuple[Response, int]:
    """Endpoint auxiliar para obtener el conteo de visitas/eventos en tiempo real."""
    total = _event_repo.count_by_site_key(site_key)
    return jsonify({"site_key": site_key, "total_events": total}), 200
