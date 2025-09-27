"""
Decorador para proteger rutas que solo pueden ser accedidas por usuarios con un cierto rol.

- role_required: Si el usuario no tiene el rol especificado en la sesión,
  muestra un mensaje y retorna un error 401 (no autorizado).
"""

from functools import wraps
from flask import session, flash, abort
from core.users import UserRole


def role_required(role: UserRole):
    """
    Decorador para vistas Flask.
    Permite el acceso solo si el usuario tiene el rol especificado.
    Si no, muestra un mensaje y retorna error 401.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verifica el rol en la sesión
            if session.get("role") != role.value:
                flash("No tenés permisos para acceder a este módulo.", "danger")
                return abort(401)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
