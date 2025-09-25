"""
Decorador para proteger rutas que solo pueden ser accedidas por administradores.

- admin_required: Si el usuario no tiene el rol "Administrador" en la sesión,
  muestra un mensaje y retorna un error 401 (no autorizado).
"""

from functools import wraps
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
