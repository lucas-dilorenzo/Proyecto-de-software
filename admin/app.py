from pathlib import Path
import sys

# 👇 Asegura que ./src esté en sys.path, para que se puedan importar `web` y `core`
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.web import create_app  # importamos la factory principal

# Flask detecta esta variable global `app` automáticamente
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
