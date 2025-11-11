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


# def api_permission_required(permission: UserPermission):
#     """
#     Decorador para API que requiere un permiso específico.
#     Si el usuario no tiene el permiso, retorna error 403 (Forbidden).
#     Si no está autenticado, retorna error 401 (Unauthorized).
#     """
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             user_id = session.get("user_id")
#             user_role = session.get("role")

#             # Verificar autenticación
#             if user_id is None or user_role is None:
#                 return jsonify({
#                     "error": {
#                         "code": "unauthorized",
#                         "message": "Authentication required"
#                     }
#                 }), 401

#             # Verificar permisos
#             if not check_permission(UserRole(user_role), permission):
#                 return jsonify({
#                     "error": {
#                         "code": "forbidden",
#                         "message": "Insufficient permissions"
#                     }
#                 }), 403

#             return f(*args, **kwargs)

#         return decorated_function

#     return decorator


# def api_optional_auth(f):
#     """
#     Decorador para API donde la autenticación es opcional.
#     Pone la información del usuario en kwargs si está autenticado.
#     """
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         user_id = session.get("user_id")
#         user_role = session.get("role")

#         # Agregar información del usuario a kwargs si está autenticado
#         kwargs['current_user_id'] = user_id
#         kwargs['current_user_role'] = UserRole(user_role) if user_role else None
#         kwargs['is_authenticated'] = user_id is not None

#         return f(*args, **kwargs)

#     return decorated_function


# def api_token_auth_required(f):
#     """
#     Decorador para API que requiere autenticación por token (Authorization header).
#     Útil para integración con clientes externos o aplicaciones móviles.

#     Ejemplo de uso:
#     Authorization: Bearer <token>
#     """
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         auth_header = request.headers.get('Authorization')

#         if not auth_header:
#             return jsonify({
#                 "error": {
#                     "code": "unauthorized",
#                     "message": "Authorization header required"
#                 }
#             }), 401

#         # Verificar formato: "Bearer <token>"
#         try:
#             auth_type, token = auth_header.split(' ', 1)
#             if auth_type.lower() != 'bearer':
#                 raise ValueError("Invalid auth type")
#         except ValueError:
#             return jsonify({
#                 "error": {
#                     "code": "unauthorized",
#                     "message": "Invalid authorization format. Use: Bearer <token>"
#                 }
#             }), 401

#         # Aquí deberías validar el token contra tu base de datos
#         # Por ahora verificamos contra un token hardcoded para ejemplo
#         if token != "your-api-token-here":
#             return jsonify({
#                 "error": {
#                     "code": "unauthorized",
#                     "message": "Invalid token"
#                 }
#             }), 401

#         return f(*args, **kwargs)

#     return decorated_function


# # Función helper para validar permisos en API
# def validate_api_permission(permission: UserPermission):
#     """
#     Función helper para validar permisos en endpoints API.
#     Retorna tuple (success: bool, error_response: dict|None, status_code: int|None)
#     """
#     user_id = session.get("user_id")
#     user_role = session.get("role")

#     if user_id is None or user_role is None:
#         return False, {
#             "error": {
#                 "code": "unauthorized",
#                 "message": "Authentication required"
#             }
#         }, 401

#     if not check_permission(UserRole(user_role), permission):
#         return False, {
#             "error": {
#                 "code": "forbidden",
#                 "message": "Insufficient permissions"
#             }
#         }, 403

#     return True, None, None
