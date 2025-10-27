"""
Controlador CRUD de usuarios para el módulo Admin.
Incluye rutas protegidas para listar, crear, editar y eliminar usuarios.
"""

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    session,
)
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
def new_user():
    """
    Muestra el formulario para crear un nuevo usuario.
    """
    # 🔹 Filtrar roles disponibles según el rol del usuario actual
    available_roles = _get_available_roles()

    return render_template(
        "users/form.html",
        user=None,
        form={},
        errors={},
        roles=available_roles,  # 🔹 Roles filtrados
        mode="create",
        action=url_for("users.create_user"),
    )


@users_bp.post("/new")
@login_required
def create_user():
    """
    Procesa el formulario de creación de usuario.
    """
    data, errors = validate_user_payload(request.form)
    if errors:
        return render_template(
            "users/form.html",
            user=None,
            form=request.form,
            errors=errors,
            roles=_get_available_roles(),  # 🔹 Roles filtrados
            mode="create",
            action=url_for("users.create_user"),
        )

    # 🔹 VALIDACIÓN BACKEND: evitar que ADMIN asigne SYS_ADMIN
    if not _can_assign_role(data["rol"]):
        flash("No tienes permisos para asignar ese rol.", "danger")
        return render_template(
            "users/form.html",
            user=None,
            form=request.form,
            errors={"rol": "No tienes permisos para asignar ese rol"},
            roles=_get_available_roles(),
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
        roles=_get_available_roles(),  # 🔹 Roles filtrados
        mode="edit",
        action=url_for("users.update_user", id=id),
    )


@users_bp.post("/<int:id>/edit")
@login_required
def update_user(id: int):
    """
    Procesa el formulario de edición de usuario.
    """
    user = users.get_user_by_id(id)
    if not user:
        abort(404)

    data, errors = validate_user_payload(request.form, editing=True)
    if errors:
        for e in errors:
            flash(e, "danger")
        return redirect(url_for("users.edit_user", id=id))

    # 🔹 VALIDACIÓN BACKEND: evitar que ADMIN asigne SYS_ADMIN
    if data.get("rol") and not _can_assign_role(data["rol"]):
        flash("No tienes permisos para asignar ese rol.", "danger")
        return redirect(url_for("users.edit_user", id=id))

    # 🔹 VALIDACIÓN: evitar que ADMIN modifique a otro SYS_ADMIN
    if (
        user.rol == UserRole.SYS_ADMIN.value
        and session.get("role") != UserRole.SYS_ADMIN.value
    ):
        flash("No tienes permisos para editar a un SYS_ADMIN.", "danger")
        return redirect(url_for("users.list_users"))

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
def delete_user(id: int):
    """
    Elimina un usuario por su ID.
    """
    user = users.get_user_by_id(id)
    if not user:
        abort(404)

    # 🔹 VALIDACIÓN: evitar que ADMIN elimine a SYS_ADMIN
    if (
        user.rol == UserRole.SYS_ADMIN.value
        and session.get("role") != UserRole.SYS_ADMIN.value
    ):
        flash("No tienes permisos para eliminar a un SYS_ADMIN.", "danger")
        return redirect(url_for("users.list_users"))

    users.delete_user(user)
    flash("Usuario eliminado.", "info")
    return redirect(url_for("users.list_users"))


@users_bp.get("/<int:id>")
@login_required
# @permission_required(UserPermission.USER_LIST)
def show_user(id: int):
    """
    Muestra la ficha de un usuario.
    """
    user = users.get_user_by_id(id)
    if not user:
        abort(404)
    return render_template("users/show.html", user=user)


# 🔹 FUNCIONES HELPER


def _get_available_roles():
    """
    Devuelve los roles que el usuario actual puede asignar.
    SYS_ADMIN solo puede ser asignado por otro SYS_ADMIN.
    """
    current_role = session.get("role")

    # Si el usuario es SYS_ADMIN, puede asignar todos los roles
    if current_role == UserRole.SYS_ADMIN.value:
        return [r.value for r in UserRole]

    # Si es ADMIN, puede asignar todos EXCEPTO SYS_ADMIN
    return [r.value for r in UserRole if r != UserRole.SYS_ADMIN]


def _can_assign_role(role_value: str) -> bool:
    """
    Verifica si el usuario actual puede asignar el rol dado.
    """
    current_role = session.get("role")

    # SYS_ADMIN puede asignar cualquier rol
    if current_role == UserRole.SYS_ADMIN.value:
        return True

    # ADMIN NO puede asignar SYS_ADMIN
    if role_value == UserRole.SYS_ADMIN.value:
        return False

    return True
