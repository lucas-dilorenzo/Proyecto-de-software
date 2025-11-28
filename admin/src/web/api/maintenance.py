from flask import jsonify
from . import api_bp


@api_bp.route("/flags/status", methods=["GET"])
def get_flags_status():
    """Obtiene el estado actual de los flags relevantes para el frontend."""
    from src.core.featureFlags import FeatureFlag

    is_maintenance_mode = FeatureFlag.get("portal_maintenance_mode")
    reviews_enabled = FeatureFlag.get("reviews_enabled")

    response = {
        "data": {
            "maintenance_mode": (
                is_maintenance_mode.value_bool if is_maintenance_mode else False
            ),
            "reviews_enabled": reviews_enabled.value_bool if reviews_enabled else False,
        }
    }
    return jsonify(response)
