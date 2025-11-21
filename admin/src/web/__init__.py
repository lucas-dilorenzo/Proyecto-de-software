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
    g,
)
import json
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
from src.core import historicalSites

# Utilidades
from sqlalchemy import select
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

from src.web.controllers.users import users_bp
from web.controllers.auth.authenticate import auth_bp
from src.web.controllers.tags_controller import tags_bp
from src.web.controllers.sites import historical_sites_bp
from src.web.controllers.sites import (
    get_categories,
    get_category_label,
    get_conservation_statuses,
    get_conservation_status,
)
from src.web import helpers
from src.web.helpers import login_required
from src.web.auditoria import site_events
from src.core.featureFlags.flag import FeatureFlag
from src.web.controllers.feature_flags import feature_flags_bp
from src.web.controllers.maintenance import maintenance_bp
from web.controllers.reseñas_controller import reseñas_bp
from src.web.storage import storage
from src.web.api import api_bp
from flask_cors import CORS
from flask_jwt_extended import JWTManager

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


def create_app(env: str = "development", static_folder: str = "../../static") -> Flask:
    app = Flask(__name__, static_folder=static_folder)

    # Cargar configuración según el entorno
    app.config.from_object(config_map.get(env, config_map["development"]))

    # Inicializar base de datos (flask_sqlalchemy_lite)
    database.init_app(app)

    # Inicializar almacenamiento (MinIO)
    storage.init_app(app)

    # Protección CSRF
    csrf = CSRFProtect(app)
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["WTF_CSRF_ENABLED"] = False

    # Server Side session
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Habilitar CORS para la API y rutas de autenticación
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}, r"/auth/*": {"origins": "*"}},
        supports_credentials=True,
    )

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = [
            "http://localhost:5173",
            "https://grupo37.proyecto2025.linti.unlp.edu.ar",
        ]
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    # JWT setup for API authentication
    app.config["JWT_SECRET_KEY"] = "super-secret"  # Cambiar en producción
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"
    app.config["JWT_COOKIE_SECURE"] = False  # Permitir cookies sin HTTPS en desarrollo
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Desactivar CSRF en desarrollo
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"  # Permitir cookies cross-site
    jwt = JWTManager(app)

    @app.route("/")
    @login_required
    def home():
        sites = historicalSites.list_all_sites()
        # Serializar los sitios para JavaScript
        sites_json = json.dumps([site.to_dict() for site in sites])
        return render_template("home.html", sites=sites_json)

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
    app.register_blueprint(feature_flags_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(reseñas_bp)
    app.register_blueprint(api_bp)  # Ya está aquí, solo faltaba el import arriba

    # Handlers de error
    app.register_error_handler(404, error_handlers.not_found)
    app.register_error_handler(401, error_handlers.unauthorized)
    app.register_error_handler(500, error_handlers.generic)

    # Definir is_sys_admin aquí, antes de usarla
    def is_sys_admin(session):
        """Verifica si el usuario tiene rol SYS_ADMIN"""
        if not session or not session.get("role"):
            return False

        # Dependiendo de cómo almacenes el rol, una de estas opciones funcionará:
        if hasattr(session["role"], "name"):
            return session["role"].name == "SYS_ADMIN"
        if hasattr(session["role"], "value"):
            return session["role"].value == "Administrador del Sistema"

        # Si es solo un string
        return session["role"] == "SYS_ADMIN"

    # Funciones que se exportan al contexto de Jinja2
    # Esta primera funcion me va a ayudar a identificar la sesion de un usuario
    app.jinja_env.globals.update(is_authenticated=authenticate.authenticated)
    app.jinja_env.globals.update(get_user=helpers.get_user_by_id)
    app.jinja_env.globals.update(get_sites_categories=get_categories)
    app.jinja_env.globals.update(get_conservation_status=get_conservation_statuses)
    app.jinja_env.globals.update(get_conservation_status_label=get_conservation_status)
    app.jinja_env.globals.update(get_category_label=get_category_label)
    app.jinja_env.globals.update(is_sys_admin=is_sys_admin)
    app.jinja_env.globals.update(image_url=helpers.get_image_url)
    app.jinja_env.globals.update(get_main_image=helpers.get_main_image_by_site)
    app.jinja_env.globals.update(
        get_secondary_image_urls=helpers.get_secondary_image_urls
    )

    # ---------- Guard global: Admin Maintenance Mode ----------
    @app.before_request
    def admin_maintenance_guard():
        path = request.path

        # Rutas que siempre están permitidas
        exempt_paths = [
            "/auth/login",
            "/auth/logout",
            "/static/",
            "/admin/maintenance",
            "/_dev/",
        ]

        # No bloquear rutas permitidas
        if any(path.startswith(exempt) for exempt in exempt_paths):
            return

        # Comprobar si es SYS_ADMIN
        user_is_sys_admin = is_sys_admin(session)

        # Permitir acceso a SYS_ADMIN al panel de feature flags incluso en mantenimiento
        if path.startswith("/admin/feature-flags") and user_is_sys_admin:
            return

        # Obtener el flag de mantenimiento
        flag = FeatureFlag.get("admin_maintenance_mode")
        maintenance_active = flag and flag.value_bool

        if maintenance_active:
            # Configurar mensaje para la UI
            g.maintenance_message = flag.message
            session["maintenance_message"] = flag.message

            # IMPORTANTE: Bloquear TODAS las rutas administrativas excepto /auth/login
            # Las rutas públicas (/sites, /, etc.) siguen permitidas
            # Revisar si es una ruta que necesita ser protegida
            protected_routes = [
                "/admin/",  # Rutas de admin tradicionales
                "/users/",  # Usuarios
                "/tags/",  # Tags
                "/sites/",  # Añadido: Ruta principal de sitios
                "/sites/admin/",  # Gestión de sitios específica
                "/historicalsites/admin/",  # Otra posible ruta de sitios
            ]

            # Bloquear acceso si es ruta protegida y no es SysAdmin
            if (
                any(path.startswith(route) for route in protected_routes)
                and not user_is_sys_admin
            ):
                return redirect(url_for("maintenance.admin"))
        else:
            # Limpiar mensaje si no hay mantenimiento
            if "maintenance_message" in session:
                session.pop("maintenance_message")
            g.maintenance_message = None

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
    # script para rearmar la db
    # -------------------------
    @app.cli.command("rearmar-db")
    def rearmar_db():
        """Resetea y siembra la base de datos (reset + roles + users + seed-db).

        Llamamos directamente a las funciones de `database` y `seeds`
        en vez de invocar las funciones registradas como comandos CLI
        para evitar problemas con el contexto o el registro de comandos.
        """
        # before seeding, we remove events to avoid errors
        from sqlalchemy import event, inspect
        from src.core.historicalSites.site import Site, SiteLog
        from src.web.auditoria.site_events import after_insert, after_update

        event.remove(Site, "after_insert", after_insert)
        event.remove(Site, "after_update", after_update)

        # resetear la base
        database.reset_db()

        # sembrar roles y usuarios y datos adicionales
        seeds.roles()
        seeds.users()
        seeds.run()

        print("DB rearmada: reset + roles + users + seed_db ejecutados.")

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
    # @app.get("/_dev/login")
    # def login_as_admin():
    #     """
    #     SOLO DESARROLLO:
    #     Setea en sesión el rol dado para poder probar el módulo de usuarios.
    #     """
    #     session["role"] = request.args.get("role", UserRole.SYS_ADMIN.name)
    #     flash("Sesión DEV iniciada.", "success")
    #     return redirect(url_for("home"))

    return app
