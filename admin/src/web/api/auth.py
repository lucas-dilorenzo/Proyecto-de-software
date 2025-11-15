"""
Decoradores de autenticación y autorización para API REST.
"""

from functools import wraps
from flask import session, jsonify, request
from src.core.permissions import check_permission
from src.core.users.user import UserRole
from src.core.permissions.permission import UserPermission


def api_auth_required(f):
    """
    Decorador para API que requiere autenticación.
    Si el usuario no está autenticado, retorna error 401 (Unauthorized).
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Buscar en las claves correctas según tu sistema de sesiones
        user_id = session.get("user")
        user_role = session.get("role")

        if user_id is None or user_role is None:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "unauthorized",
                            "message": "Authentication required",
                        }
                    }
                ),
                401,
            )

        return f(*args, **kwargs)

    return decorated_function
