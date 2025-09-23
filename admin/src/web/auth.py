from functools import wraps
from flask import session, flash, abort


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "Administrador":
            flash("No tenés permisos para acceder a este módulo.", "danger")
            return abort(401)
        return fn(*args, **kwargs)

    return wrapper
