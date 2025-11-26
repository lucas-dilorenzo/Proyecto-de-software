from flask import (
    request,
    make_response,
    jsonify,
    url_for,
    redirect,
    session,
    flash,
    current_app,
)
from werkzeug.security import check_password_hash
from src.core import users
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask import jsonify
from . import api_bp
from werkzeug.security import generate_password_hash


@api_bp.post("/auth/login_jwt")
def login_jwt():
    """Handles JWT-based user login.
    Expects JSON with "email" and "password".
    Returns:
        201 with JWT cookies on success, 401 on failure.
    """
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    user = users.get_user_by_email(email)

    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        response = make_response(
            jsonify({"access_token": access_token, "user_id": user.id}), 201
        )
        set_access_cookies(response, access_token)
        return response
    else:
        return jsonify(message="Unauthorized"), 401


@api_bp.get("/auth/logout_jwt")
@jwt_required()
def logout_jwt():
    """Handles JWT-based user logout.
    Returns:
        200 on success."""
    response = jsonify()
    unset_jwt_cookies(response)
    return response, 200


@api_bp.get("/auth/user_jwt")
@jwt_required()
def user_jwt():
    """Retrieves the authenticated user via JWT.
    Returns:
        200 with user data on success."""
    current_user = get_jwt_identity()
    user = users.get_jwt_user_by_id(current_user)
    response = jsonify(user)
    return response, 200


@api_bp.route("/auth/google/login")
def api_google_login():
    """Inicia el flujo de autenticación con Google OAuth para la API pública.
    Redirige al usuario a Google para autenticarse.
    """
    oauth = current_app.extensions.get("authlib.integrations.flask_client")

    if not oauth:
        return jsonify(message="OAuth no configurado correctamente"), 500

    redirect_uri = url_for("api.api_google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@api_bp.route("/auth/google/callback")
def api_google_callback():
    """Callback de Google OAuth para la API pública.

    Flujo:
    - Si el usuario existe: genera JWT y lo devuelve
    - Si no existe: crea el usuario automáticamente con rol PUBLIC y genera JWT

    Returns:
        JSON con access_token y user_id, o error 401
    """
    oauth = current_app.extensions.get("authlib.integrations.flask_client")

    if not oauth:
        return jsonify(message="OAuth no configurado correctamente"), 500

    try:
        token = oauth.google.authorize_access_token()
        # Obtener información del usuario directamente del endpoint de userinfo
        # en lugar de parsear el id_token (que requiere nonce)
        resp = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo")
        userinfo = resp.json()

        if not userinfo or "email" not in userinfo:
            return jsonify(message="No se pudo obtener información de Google"), 401

        email = userinfo["email"]
        user = users.get_user_by_email(email)

        # Si el usuario NO existe, lo creamos automáticamente
        if not user:
            user = users.create_user(
                email=email,
                nombre=userinfo.get("given_name", "Usuario"),
                apellido=userinfo.get("family_name", "Google"),
                password_hash=generate_password_hash(email),  # Password temporal
                rol="PUBLIC",
                activo=True,
            )

        # Verificar que el usuario esté activo
        if not user.activo:
            return jsonify(message="Usuario bloqueado"), 401

        # Generar JWT token (compatible con login nativo)
        access_token = create_access_token(identity=str(user.id))
        response = make_response(
            jsonify(
                {
                    "access_token": access_token,
                    "user_id": user.id,
                    "message": "Login exitoso con Google",
                }
            ),
            201,
        )
        set_access_cookies(response, access_token)
        return response

    except Exception as e:
        return jsonify(message=f"Error en autenticación: {str(e)}"), 401
