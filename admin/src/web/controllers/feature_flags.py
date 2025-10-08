from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.web.helpers import login_required
from src.core.featureFlags.flag import FeatureFlag
from src.core.users.user import UserRole
from datetime import datetime, timezone
import logging

feature_flags_bp = Blueprint(
    "feature_flags", __name__, url_prefix="/admin/feature-flags"
)


def _is_sys_admin() -> bool:
    """Verifica si el usuario actual tiene rol SYS_ADMIN"""
    role = session.get("role")
    return role == UserRole.SYS_ADMIN


@feature_flags_bp.get("/")
@login_required
def index():
    # Verificar permisos
    if not _is_sys_admin():
        return ("Acceso denegado", 403)

    # Obtener flags (ahora usando el método del modelo)
    flags = FeatureFlag.get_all_with_users()
    return render_template("featureFlags/list.html", flags=flags)


@feature_flags_bp.post("/update")
def update():
    # Verificar permisos
    if not _is_sys_admin():
        return ("Acceso denegado", 403)

    key = request.form.get("key")
    requested_state = request.form.get("value_bool") == "on"
    message = (request.form.get("message") or "").strip()
    user_id = session.get("user")

    # Actualizar usando el método del modelo
    success, message_text = FeatureFlag.update(key, requested_state, message, user_id)

    # Mostrar resultado
    if success:
        flash(message_text, "success")

        # Si es mantenimiento, guardar en sesión
        if key == "admin_maintenance_mode" and requested_state:
            session["maintenance_message"] = message
            session["maintenance_activated_at"] = datetime.now(timezone.utc).isoformat()
    else:
        flash(message_text, "warning")

    # Registrar en log
    logger = logging.getLogger(__name__)
    logger.info(
        f"Feature Flag {key} actualizado a {requested_state} por usuario {user_id}: {message_text}"
    )

    return redirect(url_for("feature_flags.index"))
