# imports habituales de Flask (usados por la factory y las rutas DEV)
from src.core.users.user import UserRole
from flask import (
    Flask,
    render_template,
    abort,
    request,
    session,
    redirect,
    url_for,
    flash,
)
from web.controllers.auth import authenticate

# config local (usamos alias config_map para claridad)
from .config import config as config_map

# handlers de error (mantener compatibilidad con development)
from .handlers import error as error_handlers

# DB/core - Importar desde src/core
from src.core import database

from src.web import seeds  # Importar el módulo correctamente

# Modelos
# from src.core.users import User, UserRole

# Utilidades
from sqlalchemy import select
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from src.web.controllers.users import users_bp
from web.controllers.auth.authenticate import auth_bp
from src.web.controllers.tags_controller import tags_bp
from src.web.controllers.sites import historical_sites_bp
from src.web.controllers.sites import get_categories, get_conservation_statuses
from src.web import helpers
from src.web.helpers import login_required

"""
    Crea la aplicación Flask.
    Parámetros:
    - env: str → entorno de ejecución (development, production, etc.)
    - static_folder: str → ruta a la carpeta de archivos estáticos.
        ⚠️ IMPORTANTE:
        Cambiar la ruta relativa dependiendo el SO que uses para probar la app localmente.
        # macOS/Linux → usar "../../static"
        # Windows     → usar r"..\\..\\static" (doble barra invertida o raw string)
"""


def create_app(env: str = "production", static_folder: str = "../../static") -> Flask:
    app = Flask(__name__, static_folder=static_folder)

    # Cargar configuración según el entorno
    app.config.from_object(config_map.get(env, config_map["production"]))
    print(app.config["SQLALCHEMY_DATABASE_URI"])
    print(app.config["DB_HOST"])
    # Inicializar base de datos (flask_sqlalchemy_lite)
    database.init_app(app)

    # Protección CSRF
    csrf = CSRFProtect(app)
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["WTF_CSRF_ENABLED"] = False

    # Server Side session
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    @app.route("/")
    @login_required
    def home():
        return render_template("home.html")

    @app.get("/private")
    def private():
        abort(401)

    @app.get("/error")
    def trigger_error():
        abort(500)

    # register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(historical_sites_bp)

    # Handlers de error
    app.register_error_handler(404, error_handlers.not_found)
    app.register_error_handler(401, error_handlers.unauthorized)
    app.register_error_handler(500, error_handlers.generic)

    # Funciones que se exportan al contexto de Jinja2
    # Esta primera funcion me va a ayudar a identificar la sesion de un usuario
    app.jinja_env.globals.update(is_authenticated=authenticate.authenticated)
    app.jinja_env.globals.update(get_user=helpers.get_user_by_id)
    app.jinja_env.globals.update(get_sites_categories=get_categories)
    app.jinja_env.globals.update(get_conservation_status=get_conservation_statuses)

    # -------------------------
    # Comandos CLI
    # -------------------------
    @app.cli.command("reset-db")
    def reset_db():
        """Elimina y recrea todas las tablas."""
        database.reset_db()

    @app.cli.command("seed-users")
    def seed_users():
        seeds.users()
        print("Seeds de usuarios ejecutados.")

    @app.cli.command("seed-db")
    def seed_db():
        seeds.run()

    @app.cli.command("seed-roles")
    def seed_roles():
        seeds.roles()

    # -------------------------
    # Rutas DEV utilitarias
    # -------------------------
    @app.get("/_dev/whoami")
    def whoami():
        return f"role={session.get('role')!r}"

    @app.get("/_dev/routes")
    def routes():
        def safe(rule):
            return rule.rule.replace("<", "&lt;").replace(">", "&gt;")

        return "<br>".join(sorted(safe(r) for r in app.url_map.iter_rules()))

    # -----------------------------------
    # Ruta auxiliar de DEV: login
    # -----------------------------------
    @app.get("/_dev/login")
    def login_as_admin():
        """
        SOLO DESARROLLO:
        Setea en sesión el rol dado para poder probar el módulo de usuarios.
        """
        session["role"] = request.args.get("role", UserRole.SYS_ADMIN.name)
        flash("Sesión DEV iniciada.", "success")
        return redirect(url_for("home"))

    return app
