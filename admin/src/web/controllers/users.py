from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from sqlalchemy import select, desc, asc, func
from werkzeug.security import generate_password_hash
from web.auth import admin_required
from web.validators.users import validate_user_payload
from core.database import db

try:
    from core.models import User, UserRole
except ImportError:
    from core.users import User, UserRole

users_bp = Blueprint("users", __name__, url_prefix="/admin/users")


def _clamp_per_page(val) -> int:
    try:
        n = int(val)
    except Exception:
        n = 25
    return max(1, min(n, 50))


@users_bp.get("/")
@admin_required
def list_users():
    email = (request.args.get("email") or "").strip()
    activo = (request.args.get("activo") or "").strip().upper()  # SI | NO | ""
    rol = (request.args.get("rol") or "").strip()
    order = (request.args.get("order") or "desc").lower()
    page = max(1, int(request.args.get("page") or 1))
    per_page = _clamp_per_page(request.args.get("per_page") or 25)

    stmt = select(User)
    if email:
        stmt = stmt.where(User.email.ilike(f"%{email}%"))
    if activo in ("SI", "NO"):
        stmt = stmt.where(User.activo.is_(activo == "SI"))
    if rol:
        role_enum = next((r for r in UserRole if r.value == rol), None)
        if role_enum:
            stmt = stmt.where(User.rol == role_enum)

    if order == "asc":
        stmt = stmt.order_by(asc(User.created_at))
    else:
        order = "desc"
        stmt = stmt.order_by(desc(User.created_at))

    total = db.session.scalar(select(func.count()).select_from(stmt.subquery()))
    offset = (page - 1) * per_page
    users = db.session.execute(stmt.limit(per_page).offset(offset)).scalars().all()

    roles = [r.value for r in UserRole]

    from urllib.parse import urlencode

    def qs(**overrides):
        base = dict(
            email=email,
            activo=activo,
            rol=rol,
            order=order,
            page=page,
            per_page=per_page,
        )
        base.update({k: v for k, v in overrides.items() if v is not None})
        clean = {k: v for k, v in base.items() if v not in ("", None)}
        return urlencode(clean)

    return render_template(
        "users/list.html",
        users=users,
        email=email,
        activo=activo,
        rol=rol,
        order=order,
        page=page,
        per_page=per_page,
        total=total,
        roles=roles,
        qs=qs,
    )


@users_bp.get("/new")
@admin_required
def new_user():
    return render_template(
        "users/form.html",
        user=None,
        form={},  # Agregar esto
        errors={},  # Agregar esto
        roles=[r.value for r in UserRole],
        mode="create",
        action=url_for("users.create_user"),
    )


# Cambiamos @users_bp.post("/new") a @users_bp.post("/")
@users_bp.post("/new")
@admin_required
def create_user():
    data, errors = validate_user_payload(request.form)
    if errors:
        # En lugar de redireccionar, renderizamos directamente con los datos originales
        return render_template(
            "users/form.html",
            user=None,
            form=request.form,  # Mantenemos los datos ingresados
            errors=errors,  # Mostramos los errores
            roles=[r.value for r in UserRole],
            mode="create",
            action=url_for("users.create_user"),
        )

    # Verificar email único
    exists = db.session.execute(
        select(User).where(User.email == data["email"])
    ).scalar_one_or_none()

    if exists:
        # También mantenemos los datos para este error
        flash("El email ya está registrado.", "warning")
        return render_template(
            "users/form.html",
            user=None,
            form=request.form,
            errors={"email": "Este email ya está registrado"},
            roles=[r.value for r in UserRole],
            mode="create",
            action=url_for("users.create_user"),
        )

    role_enum = next((r for r in UserRole if r.value == data["rol"]), UserRole.PUBLIC)
    activo_flag = bool(request.form.get("activo")) or data.get("activo", True)

    user = User(
        email=data["email"],
        nombre=data["nombre"],
        apellido=data["apellido"],
        password_hash=generate_password_hash(data["password"]),
        activo=activo_flag,
        rol=role_enum,
    )
    db.session.add(user)
    db.session.commit()
    flash("Usuario creado.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.get("/<int:uid>/edit")
@admin_required
def edit_user(uid: int):
    user = db.session.get(User, uid)
    if not user:
        abort(404)
    return render_template(
        "users/form.html",
        user=user,
        roles=[r.value for r in UserRole],
        mode="edit",
        action=url_for("users.update_user", uid=uid),
    )


@users_bp.post("/<int:uid>/edit")
@admin_required
def update_user(uid: int):
    user = db.session.get(User, uid)
    if not user:
        abort(404)

    data, errors = validate_user_payload(request.form, editing=True)
    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("users.edit_user", uid=uid))

    if data.get("email") and data["email"] != user.email:
        dup = db.session.execute(
            select(User).where(User.email == data["email"])
        ).scalar_one_or_none()
        if dup:
            flash("El email ya está en uso.", "warning")
            return redirect(url_for("users.edit_user", uid=uid))

    if data.get("email"):
        user.email = data["email"]
    user.nombre = data["nombre"]
    user.apellido = data["apellido"]
    if data.get("password"):
        user.password_hash = generate_password_hash(data["password"])
    if request.form.get("activo") is not None:
        user.activo = bool(request.form.get("activo"))
    if data.get("rol"):
        role_enum = next((r for r in UserRole if r.value == data["rol"]), user.rol)
        user.rol = role_enum

    db.session.commit()
    flash("Usuario actualizado.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.post("/<int:uid>/delete")
@admin_required
def delete_user(uid: int):
    user = db.session.get(User, uid)
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado.", "info")
    return redirect(url_for("users.list_users"))
