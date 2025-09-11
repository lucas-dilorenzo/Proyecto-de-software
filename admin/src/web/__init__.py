from flask import Flask
from flask import render_template

"""
Crea la aplicación Flask.

Parámetros:
- env: str → entorno de ejecución (development, production, etc.)
- static_folder: str → ruta a la carpeta de archivos estáticos.

    ⚠️ IMPORTANTE:
    Cambiar la ruta relativa dependiendo el SO que uses para probar la app localmente.
    # macOS/Linux → usar "../../static"
    # Windows     → usar r"..\..\static" (doble barra invertida o raw string)
"""
def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    @app.route('/')
    def home():
        return render_template('home.html')
    
    return app
