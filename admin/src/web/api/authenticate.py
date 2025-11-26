from core.users.user import UserRole
from flask import (
    request,
    make_response,
    jsonify,
    url_for,
    redirect,
    session,
    flash,
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
from src.web import oauth
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


@api_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("google_auth_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@api_bp.route("/auth/google/callback")
def google_auth_callback():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(token)
    user = users.get_user_by_email(userinfo["email"])
    if userinfo:
        session["user"] = userinfo["email"]
        session["role"] = user.role if user else UserRole.PUBLIC
        flash(f"Bienvenido, {userinfo['given_name']}!", "success")
        return redirect(url_for("home"))
    flash("No se pudo autenticar con Google.", "danger")
    return redirect(url_for("auth.login"))


@api_bp.route("/logout/google")
def logout_google():
    session.clear()
    flash("Sesión cerrada correctamente.")
    return redirect(url_for("home"))


@api_bp.route("/auth/google/register")
def google_register():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(token)
    if userinfo:
        # Verifica que el email no esté registrado
        exists = users.user_exists(userinfo["email"])

        if exists:
            flash("El email ya está registrado.", "warning")
            return redirect(url_for("auth.login"))

        users.create_user(
            email=userinfo["email"],
            nombre=userinfo["given_name"],
            apellido=userinfo["family_name"],
            password_hash=generate_password_hash(token),
            rol=UserRole.PUBLIC,
            activo=True,
        )
        flash("Usuario creado.", "success")
        flash(f"Registro exitoso, {userinfo['name']}!", "success")
        return redirect(url_for("home"))
    flash("No se pudo registrar con Google.", "danger")
    return redirect(url_for("auth.register"))
