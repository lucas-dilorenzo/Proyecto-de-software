from flask import redirect, render_template, request, session, url_for, Blueprint, flash
from werkzeug.security import check_password_hash
from core.users import User, UserRole
from web.helpers.validations.auth import FormularioInicioSesion
from web.helpers import is_authenticated

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
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
    # del session["user"]
    session.clear()
    flash("La sesión se cerró correctamente.")
    return redirect(url_for("home"))


def authenticated(session):
    return session.get("user")
