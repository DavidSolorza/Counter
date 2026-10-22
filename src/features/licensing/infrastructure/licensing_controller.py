"""
Controlador HTTP Flask para el módulo de Licenciamiento.
Gobernanza: Límite estricto < 150 líneas.
"""
from flask import Blueprint, request, jsonify, Response
from src.features.licensing.infrastructure.sqlite_site_repository import SqliteSiteRepository
from src.features.licensing.application.verify_license_use_case import VerifyLicenseUseCase
from src.core.errors.exceptions import AppException

licensing_bp = Blueprint("licensing", __name__, url_prefix="/api/v1")
_repository = SqliteSiteRepository()
_verify_use_case = VerifyLicenseUseCase(_repository)


@licensing_bp.route("/verify", methods=["POST"])
def verify_site_key() -> tuple[Response, int]:
    """Endpoint para autenticación de licencia y handshake del SDK."""
    payload = request.get_json(silent=True) or {}
    site_key = payload.get("site_key")
    client_domain = request.headers.get("Origin") or request.host

    try:
        result = _verify_use_case.execute(site_key, client_domain)
        return jsonify({
            "valid": result.valid,
            "message": result.message,
            "domain": result.domain
        }), 200
    except AppException as ex:
        return jsonify({
            "valid": False,
            "error": ex.message
        }), ex.status_code
    except Exception:
        return jsonify({
            "valid": False,
            "error": "Error interno al verificar la licencia."
        }), 500
