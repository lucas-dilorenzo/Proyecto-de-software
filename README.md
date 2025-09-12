# Proyecto Grupo37

Este proyecto contiene dos aplicaciones independientes:
- **Admin**: Una aplicación web desarrollada con Flask
- **Calculadora**: Una aplicación de consola para operaciones matemáticas básicas

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

- **Python 3.12 o superior**
- **Poetry** (para gestión de dependencias del módulo admin)

### Instalación de Poetry

**En macOS/Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

O en macOS con Homebrew:
```bash
brew install poetry
```

**En Windows:**

Opción 1 - PowerShell:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Opción 2 - Con pip:
```cmd
pip install poetry
```

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd code
```

### 2. Configurar el módulo Admin (Aplicación Web)

```bash
cd admin
poetry install
```

## ▶️ Cómo Ejecutar las Aplicaciones

### Aplicación Web (Admin)

1. Navegar al directorio admin:
```bash
cd admin
```

2. Activar el entorno virtual de Poetry:
```bash
poetry env activate
```
Esto te dará el comando específico para activar el entorno virtual en tu sistema.

3. Ejecutar la aplicación:
```bash
python main.py
```

4. Abrir tu navegador y visitar: `http://127.0.0.1:5000`

### Calculadora

La calculadora no requiere configuración adicional, solo Python.

1. Navegar al directorio calculadora:
```bash
cd calculadora
```

2. Ejecutar la aplicación:
```bash
python main.py
```

3. Seguir las instrucciones en pantalla para realizar cálculos.

## 🧪 Ejecutar Tests

Para ejecutar los tests del módulo admin:

```bash
cd admin
poetry run pytest
```

## 📁 Estructura del Proyecto

```
code/
├── README.md
├── admin/                      # Aplicación web Flask
│   ├── main.py                # Punto de entrada de la app web
│   ├── pyproject.toml         # Configuración de Poetry y dependencias
│   ├── poetry.lock           # Lock file de dependencias
│   ├── src/
│   │   └── web/
│   │       ├── __init__.py   # Factory de la aplicación Flask
│   │       └── templates/    # Templates HTML
│   ├── static/               # Archivos estáticos (CSS, JS, imágenes)
│   └── tests/               # Tests unitarios
└── calculadora/              # Aplicación de consola
    ├── main.py              # Punto de entrada de la calculadora
    └── src/
        ├── calculadora.py   # Lógica principal de la calculadora
        └── operaciones.py   # Operaciones matemáticas básicas
```

## 🔧 Solución de Problemas

### Error de rutas estáticas en Windows

Si estás usando Windows y tienes problemas con los archivos estáticos, modifica el archivo `admin/src/web/__init__.py`:

```python
# Cambiar esta línea:
def create_app(env="development", static_folder="../../static"):

# Por esta (para Windows):
def create_app(env="development", static_folder=r"..\..\static"):
```

### Python no encontrado

Asegúrate de que Python esté en tu PATH. Puedes verificarlo con:
```bash
python --version
# o
python3 --version
```