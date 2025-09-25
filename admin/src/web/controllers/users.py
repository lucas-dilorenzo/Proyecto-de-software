"""
Controlador CRUD de usuarios para el módulo Admin.
Incluye rutas protegidas para listar, crear, editar y eliminar usuarios.
"""

from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from sqlalchemy import select, desc, asc, func
from werkzeug.security import generate_password_hash
from web.auth import admin_required
from web.validators.users import validate_user_payload
# from core.database import db
from src.core.database import db
from core.users import User, UserRole

# Define el blueprint para las rutas de usuarios bajo /admin/users
users_bp = Blueprint("users", __name__, url_prefix="/admin/users")


def _clamp_per_page(val) -> int:
    """
    Limita la cantidad de resultados por página entre 1 y 50.
    """
    try:
        n = int(val)
    except Exception:
        n = 25
    return max(1, min(n, 50))


@users_bp.get("/")
@admin_required
def list_users():
    """
    Listado de usuarios con filtros por email, activo, rol y orden.
    Soporta paginación.
    """
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

    # Total de usuarios para paginación
    total = db.session.scalar(select(func.count()).select_from(stmt.subquery()))
    offset = (page - 1) * per_page
    users = db.session.execute(stmt.limit(per_page).offset(offset)).scalars().all()

    roles = [r.value for r in UserRole]

    from urllib.parse import urlencode

    def qs(**overrides):
        """
        Genera la query string para mantener los filtros y paginación en los links.
        """
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
    """
    Muestra el formulario para crear un nuevo usuario.
    """
    return render_template(
        "users/form.html",
        user=None,
        form={},  # Formulario vacío
        errors={},  # Sin errores iniciales
        roles=[r.value for r in UserRole],
        mode="create",
        action=url_for("users.create_user"),
    )


@users_bp.post("/new")
@admin_required
def create_user():
    """
    Procesa el formulario de creación de usuario.
    Si hay errores, los muestra y mantiene los datos ingresados.
    Si el email ya existe, muestra advertencia.
    Si todo es correcto, crea el usuario y redirige al listado.
    """
    data, errors = validate_user_payload(request.form)
    if errors:
        return render_template(
            "users/form.html",
            user=None,
            form=request.form,
            errors=errors,
            roles=[r.value for r in UserRole],
            mode="create",
            action=url_for("users.create_user"),
        )

    # Verifica que el email no esté registrado
    exists = User.query.filter_by(email=data["email"]).first()

    if exists:
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
    """
    Muestra el formulario para editar un usuario existente.
    """
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
    """
    Procesa el formulario de edición de usuario.
    Si hay errores, redirige mostrando los mensajes.
    Si el email ya existe en otro usuario, muestra advertencia.
    Si todo es correcto, actualiza el usuario y redirige al listado.
    """
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
    """
    Elimina un usuario por su ID.
    """
    user = db.session.get(User, uid)
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado.", "info")
    return redirect(url_for("users.list_users"))
