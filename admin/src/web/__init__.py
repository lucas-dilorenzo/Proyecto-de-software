# imports habituales de Flask (usados por la factory y las rutas DEV)
from flask import Flask, render_template, abort, session, redirect, url_for, flash

# config local (usamos alias config_map para claridad)
from .config import config as config_map

# handlers de error (mantener compatibilidad con development)
from .handlers import error as error_handlers

# DB/core - Opción B: import desde el paquete instalado en src/
from core import database
from core.database import db

from src.web import seeds  # Importar el módulo correctamente

# Modelos
from core.users import User, UserRole

# Utilidades
from sqlalchemy import select

from web.controllers.users import users_bp

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

    # Register blueprints
    app.register_blueprint(tags_bp)

    app.register_blueprint(sites.historical_sites_bp)

    @app.route("/")
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

    # Handlers de error
    app.register_error_handler(404, error_handlers.not_found)
    app.register_error_handler(401, error_handlers.unauthorized)
    app.register_error_handler(500, error_handlers.generic)

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
    # Ruta auxiliar de DEV: login Admin
    # -----------------------------------
    @app.get("/_dev/login_as_admin")
    def login_as_admin():
        """
        SOLO DESARROLLO:
        Setea en sesión el rol 'Administrador' para poder probar el módulo de usuarios.
        """
        session["role"] = "Administrador"
        flash("Sesión DEV: ingresaste como Administrador.", "success")
        return redirect(url_for("home"))

    return app
