"""
Controlador CRUD de usuarios para el módulo Admin.
Incluye rutas protegidas para listar, crear, editar y eliminar usuarios.
"""

from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from sqlalchemy import select, desc, asc, func
from werkzeug.security import generate_password_hash
from src.web.auth import permission_required
from src.web.validators.users import validate_user_payload
from src.web.helpers import login_required

# from core.database import db
from src.core.users import UserRole
from src.core import users
from src.core.permissions.permission import UserPermission

# Define el blueprint para las rutas de usuarios bajo /admin/users
users_bp = Blueprint("users", __name__, url_prefix="/admin/users")


@users_bp.before_request
@permission_required(UserPermission.USER_MODULE)
def bp_guard():
    pass


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
@login_required
# @permission_required(UserPermission.USER_LIST)
def list_users():
    # Recuperar parámetros de filtrado
    email = (request.args.get("email") or "").strip()
    activo = (request.args.get("activo") or "").strip().upper()  # SI | NO | ""
    rol = (request.args.get("rol") or "").strip()
    order = (request.args.get("order") or "desc").lower()
    page = max(1, int(request.args.get("page") or 1))
    per_page = _clamp_per_page(request.args.get("per_page") or 25)

    # Usar la función get_users_filtered del modelo
    usersList = users.get_users_filtered(
        page=page,
        per_page=per_page,
        email=email,
        activo=activo,
        rol=rol,
        order=order,
    )

    # Pasar todos los parámetros al template para mantener el estado de los filtros
    return render_template(
        "users/list.html",
        users=usersList,
        email=email,
        activo=activo,
        rol=rol,
        order=order,
        page=page,
        per_page=per_page,
        roles=[r.value for r in UserRole],
    )


@users_bp.get("/new")
@login_required
# @permission_required(UserPermission.USER_CREATE)
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
@login_required
# @permission_required(UserPermission.USER_CREATE)
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
    exists = users.user_exists(data["email"])

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
    activo_flag = data.get("activo", True)

    users.create_user(
        email=data["email"],
        nombre=data["nombre"],
        apellido=data["apellido"],
        password_hash=generate_password_hash(data["password"]),
        rol=role_enum,
        activo=activo_flag,
    )
    flash("Usuario creado.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.get("/<int:id>/edit")
@login_required
# @permission_required(UserPermission.USER_UPDATE)
def edit_user(id: int):
    """
    Muestra el formulario para editar un usuario existente.
    """
    user = users.get_user_by_id(id)
    if not user:
        abort(404)
    return render_template(
        "users/form.html",
        user=user,
        roles=[r.value for r in UserRole],
        mode="edit",
        action=url_for("users.update_user", id=id),
    )


@users_bp.post("/<int:id>/edit")
@login_required
# @permission_required(UserPermission.USER_UPDATE)
def update_user(id: int):
    """
    Procesa el formulario de edición de usuario.
    Si hay errores, redirige mostrando los mensajes.
    Si el email ya existe en otro usuario, muestra advertencia.
    Si todo es correcto, actualiza el usuario y redirige al listado.
    """
    user = users.get_user_by_id(id)
    if not user:
        abort(404)

    data, errors = validate_user_payload(request.form, editing=True)
    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("users.edit_user", id=id))

    # if data.get("email") and data["email"] != user.email:
    #     dup = db.session.execute(
    #         select(User).where(User.email == data["email"])
    #     ).scalar_one_or_none()
    #     if dup:
    #         flash("El email ya está en uso.", "warning")
    #         return redirect(url_for("users.edit_user", id=id))
    if data.get("email") and data["email"] != user.email:
        if not users.validate_email_unique(data["email"], user_id=user.id):
            flash("El email ya está en uso.", "warning")
            return redirect(url_for("users.edit_user", id=id))

    if data.get("email"):
        user.email = data["email"]
    user.nombre = data["nombre"]
    user.apellido = data["apellido"]
    if data.get("password"):
        user.password_hash = generate_password_hash(data["password"])
    if "activo" in data:  # data ya tiene el booleano correcto del validador
        if not data["activo"] and user.rol in [UserRole.ADMIN, UserRole.SYS_ADMIN]:
            flash("No se puede desactivar un usuario Administrador.", "danger")
            return redirect(url_for("users.edit_user", id=id))
        user.activo = data["activo"]
    if data.get("rol"):
        role_enum = next((r for r in UserRole if r.value == data["rol"]), user.rol)
        user.rol = role_enum

    users.edit_user(user)
    flash("Usuario actualizado.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.post("/<int:id>/delete")
@login_required
# @permission_required(UserPermission.USER_DELETE)
def delete_user(id: int):
    """
    Elimina un usuario por su ID.
    """
    user = users.get_user_by_id(id)
    if not user:
        abort(404)
    users.delete_user(user)
    flash("Usuario eliminado.", "info")
    return redirect(url_for("users.list_users"))


@users_bp.get("/<int:id>")
@login_required
@permission_required(UserPermission.USER_LIST)
def show_user(id: int):
    """
    Muestra la ficha de un usuario.
    """
    user = users.get_user_by_id(id)
    if not user:
        abort(404)
    return render_template("users/show.html", user=user)
