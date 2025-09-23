# code/admin/src/web/__init__.py
from flask import Flask, render_template, abort, session, redirect, url_for, flash
from .config import config as config_map

# DB/core
from core import database
from core.database import db, Base

# Modelos (asegurate de tener src/core/models/user.py y __init__.py que exporte User y UserRole)
from core.models import User, UserRole

# Handlers de error (ya existen en tu proyecto)
from .handlers import error as error_handlers

# Utilidades
from werkzeug.security import generate_password_hash
from sqlalchemy import select

from web.controllers.users import users_bp


def create_app(env: str = "development", static_folder: str = "../../static") -> Flask:
    """
    Crea la aplicación Flask.

    Parámetros:
    - env: str → entorno de ejecución ("development" | "production" | "test")
    - static_folder: str → ruta a la carpeta de archivos estáticos (para dev podés usar "../../static")
    """
    app = Flask(__name__, static_folder=static_folder)

    # Cargar configuración según el entorno
    app.config.from_object(config_map.get(env, config_map["development"]))

    # Inicializar base de datos (flask_sqlalchemy_lite)
    database.init_app(app)

    # En desarrollo, creamos las tablas si no existen
    if env == "development":
        with app.app_context():
            Base.metadata.create_all(bind=db.engine)

    # -------------------------
    # Rutas de ejemplo / home
    # -------------------------
    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/private")
    def private():
        abort(401)

    @app.get("/error")
    def trigger_error():
        abort(500)

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

    # -------------------------
    # register blueprints
    # -------------------------
    app.register_blueprint(users_bp)

    # -------------------------
    # Handlers de error
    # -------------------------
    app.register_error_handler(404, error_handlers.not_found)
    app.register_error_handler(401, error_handlers.unauthorized)
    app.register_error_handler(500, error_handlers.generic)

    # -------------------------
    # Comandos CLI
    # -------------------------
    @app.cli.command("reset-db")
    def reset_db():
        """Elimina y recrea todas las tablas."""
        with app.app_context():
            Base.metadata.drop_all(bind=db.engine)
            Base.metadata.create_all(bind=db.engine)
            print("DB reseteada.")

    @app.cli.command("seed-users")
    def seed_users():
        """Crea un usuario administrador por defecto si no existe."""
        with app.app_context():
            exists = db.session.execute(
                select(User).where(User.email == "admin@example.com")
            ).scalar_one_or_none()

            if not exists:
                admin = User(
                    email="admin@example.com",
                    nombre="Admin",
                    apellido="Local",
                    password_hash=generate_password_hash("admin123"),
                    activo=True,
                    rol=UserRole.ADMIN,
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin creado: admin@example.com / admin123")
            else:
                print("El admin ya existe.")

    # -------------------------
    # Comandos CLI
    # -------------------------
    @app.get("/_dev/whoami")
    def whoami():
        return f"role={session.get('role')!r}"

    # -------------------------
    # Conformar rutas registradas
    # -------------------------
    @app.get("/_dev/routes")
    def routes():
        return "<br>".join(sorted(str(r) for r in app.url_map.iter_rules()))

    return app
