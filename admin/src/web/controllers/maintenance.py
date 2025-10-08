from flask import Blueprint, render_template
from src.core.featureFlags.flag import FeatureFlag

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/admin")


@maintenance_bp.get("/maintenance")
def admin():
    ff = FeatureFlag.get("admin_maintenance_mode")
    msg = ff.message if ff and ff.value_bool else ""
    return render_template("maintenance/admin.html", message=msg), 503
