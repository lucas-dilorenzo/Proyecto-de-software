"""
Decorador para proteger rutas que solo pueden ser accedidas por administradores.

- admin_required: Si el usuario no tiene el rol "Administrador" en la sesión,
  muestra un mensaje y retorna un error 401 (no autorizado).
"""

from functools import wraps
from src.core.permissions import check_permission

from src.core.users.user import UserRole
from src.core.permissions.permission import UserPermission
from flask import session, flash, abort


def permission_required(permission: UserPermission):
    """
    Decorador para vistas Flask.
    Permite el acceso solo si el usuario tiene el permiso especificado.
    Si no, muestra un mensaje y retorna error 401.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_role = session.get("role")
            if not check_permission(UserRole(user_role), permission):
                flash("No tenés permisos para acceder a este módulo.", "danger")
                return abort(401)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
