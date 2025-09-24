# Proyecto Grupo37

Este proyecto contiene dos aplicaciones independientes:
- **Admin**: Una aplicación web desarrollada con Flask + SQLAlchemy, gestionada con Poetry.
- **Calculadora**: Una aplicación de consola para operaciones matemáticas básicas.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

- **Python 3.12 o superior**
- **Poetry** (para gestión de dependencias del módulo Admin)

### Instalación de Poetry

**En macOS/Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

En macOS con Homebrew:
```bash
brew install poetry
```

**En Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

---

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

Esto instalará las dependencias y registrará el paquete `web` y `core`.

---

## ▶️ Cómo Ejecutar las Aplicaciones

### Aplicación Web (Admin)

1. Navegar al directorio `admin`:
```bash
cd admin
```

2. Activar el entorno virtual de Poetry:
```bash
poetry env activate
```
Esto te dará el comando específico para activar el entorno virtual en tu sistema. por ejemplo: 
```
source /Users/lucas/Desktop/PROYECTO/code/admin/.venv/bin/activate
```
Copiamos y pegamos esa linea completa y nos levantara el entrono virtual.

3. Levantar la aplicación (modo desarrollo):
```bash
poetry run flask run --debug
```

4. Abrir en el navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### Comandos útiles (Admin)

- **Resetear la base de datos (memoria / SQLite local):**
```bash
poetry run flask --app web:create_app reset-db
```

- **Crear usuario administrador inicial:**
```bash
poetry run flask --app web:create_app seed-users
```
Crea el admin `admin@example.com / admin123`.

---

### Módulo de Usuarios (Admin)

Accesible solo para **rol Administrador**.

- **Login de desarrollo (setea rol en sesión):**
  ```
  http://127.0.0.1:5000/_dev/login_as_admin
  ```

- **Ver rol actual en sesión:**
  ```
  http://127.0.0.1:5000/_dev/whoami
  ```

- **Listado de usuarios:**
  ```
  http://127.0.0.1:5000/admin/users
  ```

Funcionalidades:
- CRUD completo (crear, listar, editar, eliminar).
- Filtros: email / activo (SI|NO) / rol.
- Orden por fecha de creación (asc/desc).
- Paginación server-side (máx 25 registros).
- Validaciones cliente y servidor.
- Feedback con mensajes flash.

---

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

---

## 🧪 Ejecutar Tests

Para ejecutar los tests del módulo Admin:

```bash
cd admin
poetry run pytest
```

## 🔧 Solución de Problemas

### Error de rutas estáticas en Windows

Si estás usando Windows y tienes problemas con los archivos estáticos, modifica:

```python
# En admin/src/web/__init__.py
def create_app(env="development", static_folder="../../static"):
# Por esta versión en Windows:
def create_app(env="development", static_folder=r"..\..\static"):
```

### Python no encontrado

Asegúrate de que Python esté en tu PATH:
```bash
python --version
# o
python3 --version
```
