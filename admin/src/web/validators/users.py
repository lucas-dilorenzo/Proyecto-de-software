"""
Validador de datos para formularios de usuario.
Esta función se usa tanto para crear como para editar usuarios.
Verifica que los campos requeridos estén presentes y tengan el formato correcto.
Devuelve dos diccionarios: uno con los datos limpios y otro con los errores encontrados.
"""

import re
from typing import Dict, Tuple, Any

# Expresión regular para validar emails simples
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_user_payload(
    data: Dict, editing: bool = False
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Valida los datos recibidos de un formulario de usuario.

    Parámetros:
      data: Diccionario con los datos del formulario.
        Espera las claves: email, nombre, apellido, password, activo, rol.
      editing: Booleano. Si es True, la contraseña es opcional (edición de usuario).

    Retorna:
      (cleaned_data, errors)
      cleaned_data: Diccionario con los datos validados y convertidos.
      errors: Diccionario con mensajes de error por campo (si los hay).
    """
    errors: Dict[str, str] = {}
    cleaned_data: Dict[str, Any] = {}

    # Limpieza y obtención de campos
    email = (data.get("email") or "").strip()
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()
    password = data.get("password") or ""
    activo = (data.get("activo") or "").strip().upper()
    rol = (data.get("rol") or "").strip()

    # Validación de email
    if not email:
        errors["email"] = "El email es requerido."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Formato de email inválido."
    else:
        cleaned_data["email"] = email

    # Validación de nombre
    if not nombre:
        errors["nombre"] = "El nombre es requerido."
    else:
        cleaned_data["nombre"] = nombre

    # Validación de apellido
    if not apellido:
        errors["apellido"] = "El apellido es requerido."
    else:
        cleaned_data["apellido"] = apellido

    # Validación de contraseña
    if not editing and not password:
        errors["password"] = "La contraseña es requerida."
    elif password:  # Solo incluir password si se proporciona (importante en edición)
        cleaned_data["password"] = password

    # Validación de campo activo (debe ser "SI" o "NO")
    if activo not in ("SI", "NO"):
        errors["activo"] = "Debe ser SI o NO."
    else:
        cleaned_data["activo"] = activo == "SI"  # Convierte a booleano

    # Validación de rol
    if rol not in ("Usuario público", "Editor", "Administrador"):
        errors["rol"] = "Rol inválido."
    else:
        cleaned_data["rol"] = rol

    return cleaned_data, errors
