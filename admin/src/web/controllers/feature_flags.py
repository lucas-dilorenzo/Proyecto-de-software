from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.web.helpers import login_required
from src.core.database import db
from src.core.featureFlags.flag import FeatureFlag
from src.core.users.user import User, UserRole
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
    # Verificar aquí si el usuario es SYS_ADMIN, no a nivel de módulo
    if not _is_sys_admin():
        return ("Acceso denegado", 403)

    flags = (
        db.session.query(FeatureFlag, User)
        .outerjoin(User, FeatureFlag.updated_by_user_id == User.id)
        .all()
    )

    for flag, user in flags:
        flag.updated_by = user

    return render_template("featureFlags/list.html", flags=[f[0] for f in flags])


@feature_flags_bp.post("/update")
def update():
    # Verificar si es SYS_ADMIN dentro de la función, no a nivel de módulo
    if not _is_sys_admin():
        return ("Acceso denegado", 403)

    key = request.form.get("key")
    requested_state = request.form.get("value_bool") == "on"
    message = (request.form.get("message") or "").strip()

    ff = FeatureFlag.get(key)
    if not ff:
        flash("Flag inválido.", "danger")
        return redirect(url_for("feature_flags.index"))

    # Siempre cambiar al estado solicitado
    ff.value_bool = requested_state

    # Validaciones
    is_maintenance = key in ("admin_maintenance_mode", "portal_maintenance_mode")
    if is_maintenance and requested_state and not message:
        flash(
            "El mensaje de mantenimiento es obligatorio cuando el modo está ON.",
            "warning",
        )
        return redirect(url_for("feature_flags.index"))
    if len(message) > 200:
        flash("El mensaje no puede superar 200 caracteres.", "warning")
        return redirect(url_for("feature_flags.index"))
    # Validación adicional para portal_maintenance_mode
    if key == "portal_maintenance_mode" and requested_state and len(message) < 10:
        flash(
            "El mensaje de mantenimiento debe ser descriptivo (mínimo 10 caracteres).",
            "warning",
        )
        return redirect(url_for("feature_flags.index"))

    ff.message = message or ""
    ff.updated_by_user_id = session.get("user")
    ff.updated_at = datetime.now(timezone.utc)

    # Al cambiar el estado:
    if key == "admin_maintenance_mode" and requested_state:
        # Guardar en session para mostrar mensaje a todos los usuarios
        session["maintenance_message"] = message
        session["maintenance_activated_at"] = datetime.now(timezone.utc).isoformat()

    # Evitar que admin_maintenance_mode y portal_maintenance_mode estén ON simultáneamente
    if requested_state and key == "admin_maintenance_mode":
        portal_flag = FeatureFlag.get("portal_maintenance_mode")
        if portal_flag and portal_flag.value_bool:
            flash(
                "No se puede activar el mantenimiento de admin mientras el portal está en mantenimiento.",
                "warning",
            )
            return redirect(url_for("feature_flags.index"))

    # Agregar registro de actividad
    logger = logging.getLogger(__name__)
    user_id = session.get("user", "unknown")
    logger.info(
        f"Feature Flag {key} cambiado a {requested_state} por usuario {user_id}"
    )

    db.session.commit()
    flash("Flag actualizado.", "success")
    return redirect(url_for("feature_flags.index"))
