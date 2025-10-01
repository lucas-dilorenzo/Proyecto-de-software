"""
Decorador para proteger rutas que solo pueden ser accedidas por administradores.

- admin_required: Si el usuario no tiene el rol "Administrador" en la sesión,
  muestra un mensaje y retorna un error 401 (no autorizado).
"""

from functools import wraps
from src.core.permissions import check_permission
from src.core.permissions.permission import UserPermission
from flask import session, flash, abort


def admin_required(fn):
    """
    Decorador para vistas Flask.
    Permite el acceso solo si el usuario tiene rol de Administrador.
    Si no, muestra un mensaje y retorna error 401.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verifica el rol en la sesión
        if session.get("role") != "Administrador":
            flash("No tenés permisos para acceder a este módulo.", "danger")
            return abort(401)
        return fn(*args, **kwargs)

    return wrapper


def permission_required(name: UserPermission):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if check_permission(session.get("role"), name):
                return fn(*args, **kwargs)
            else:
                flash("No tenés permisos para acceder a este módulo.", "danger")
                abort(401)

        return wrapper

    return decorator
