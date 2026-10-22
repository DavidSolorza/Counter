"""
backend/controllers/licensing_controller.py
Controlador para el endpoint de Handshake y verificación de llaves.
Gobernanza: Límite estricto < 150 líneas.
"""
from flask import Blueprint, request, jsonify, Response
from database.repositories.site_repository import SiteRepository
from backend.core.errors import AppException

licensing_bp = Blueprint("licensing", __name__, url_prefix="/api/v1")
_site_repo = SiteRepository()


@licensing_bp.route("/verify", methods=["POST"])
def verify_site_key() -> tuple[Response, int]:
    data = request.get_json(silent=True) or {}
    site_key = data.get("site_key")

    if not site_key:
        return jsonify({"valid": False, "error": "Site Key ausente."}), 403

    site = _site_repo.find_by_key(site_key.strip())
    if not site:
        return jsonify({"valid": False, "error": "Licencia no registrada."}), 403

    if not site["is_active"]:
        return jsonify({"valid": False, "error": "Licencia suspendida/inactiva."}), 403

    return jsonify({
        "valid": True,
        "message": "Licencia activa. SDK desbloqueado.",
        "domain": site["domain"]
    }), 200
