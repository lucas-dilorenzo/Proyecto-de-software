# -------------------------------------------------------------------
# Archivo .flaskenv
# Configuración de entorno para levantar la app Flask en local
# -------------------------------------------------------------------

# Nombre del módulo/factory que Flask debe usar
# Puede ser "app" (si usás app.py) o "web:create_app" (si usás factory directa)
FLASK_APP=app

# Ambiente de ejecución (development | production)
FLASK_ENV=development

# Agregamos ./src al PYTHONPATH para que Python encuentre
# los paquetes `web` y `core` sin necesidad de usar `PYTHONPATH=src`
PYTHONPATH=src
