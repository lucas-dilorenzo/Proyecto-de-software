from flask import redirect, render_template, request, session, url_for, Blueprint, flash
from werkzeug.security import check_password_hash
from core.users import User, UserRole
from web.helpers.validations.auth import FormularioInicioSesion
from web.helpers import is_authenticated
from src.core import users
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask import jsonify

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login.
    Returns:
        Redirects to home page on successful login or renders login template on failure.
    """
    if is_authenticated(session):
        return redirect(url_for("home"))
    if request.method == "POST":
        form = FormularioInicioSesion()
        if form.validate_on_submit():
            params = request.form

            email = params.get("email")
            password = params.get("password")
            if not email or not password:
                flash("Por favor, completa todos los campos.", "warning")
                return render_template("auth/login.html", email=email)

            user = User.query.filter_by(
                email=params.get("email")
            ).first()  # <-- Esto hay que hacerlo en el modulo de usuarios implementando una funcion

            if not user:
                flash("Usuario no encontrado.", "danger")
                return render_template("auth/login.html", email=email)

            if not user.activo:
                flash("Usuario bloqueado.", "danger")
                return render_template("auth/login.html", email=email)

            if user and check_password_hash(user.password_hash, password):
                session["user"] = user.id
                session["role"] = user.rol  # Guardar el rol del usuario en la sesión
                flash(f"Bienvenido, {user.nombre}!", "success")
                return redirect(url_for("home"))
            else:
                flash("Credenciales inválidas. Intenta de nuevo.", "danger")
                return render_template("auth/login.html", email=email)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{getattr(form, field).label.text}: {error}", "danger")
            return render_template("auth/login.html")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """Handle user logout.
    Returns:
        Redirects to home page after logging out."""
    session.clear()
    flash("La sesión se cerró correctamente.")
    return redirect(url_for("home"))


def authenticated(session):
    """Retrieve the authenticated user from the session.
    Args:
        session: The current session.
    Returns:
        The authenticated user or None if not found."""
    return session.get("user")


@auth_bp.post("/login_jwt")
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
        access_token = create_access_token(identity=user.id)
        response = jsonify()
        set_access_cookies(response, access_token)
        return response, 201
    else:
        return jsonify(message="Unauthorized"), 401


@auth_bp.get("/logout_jwt")
@jwt_required()
def logout_jwt():
    """Handles JWT-based user logout.
    Returns:
        200 on success."""
    response = jsonify()
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.get("/user_jwt")
@jwt_required()
def user_jwt():
    """Retrieves the authenticated user via JWT.
    Returns:
        200 with user data on success."""
    current_user = get_jwt_identity()
    user = users.get_jwt_user_by_id(current_user)
    response = jsonify(user)
    return response, 200
