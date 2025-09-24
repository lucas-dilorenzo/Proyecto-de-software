from src.web.controllers import sites
from flask import Flask
from flask import abort
from flask import render_template
from src.core import database
from .handlers import error
from .config import config
from src.web import seeds

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


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    # Load configuration
    app.config.from_object(config[env])

    app.register_error_handler(404, error.not_found)
    app.register_error_handler(401, error.unauthorized)
    app.register_error_handler(500, error.generic)

    app.register_blueprint(sites.historical_sites_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/private")
    def private():
        abort(401)

    @app.route("/error")
    def trigger_error():
        abort(500)

    # Database setup
    database.init_app(app)

    # Register commands
    @app.cli.command("reset-db")
    def reset_db():
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db():
        seeds.run()

    return app
