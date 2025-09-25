import re
from typing import Dict, Tuple, Any

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_user_payload(
    data: Dict, editing: bool = False
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    data esperado:
      email, nombre, apellido, password(opcional en update), activo("SI"/"NO"), rol(...)

    Returns:
      (cleaned_data, errors)
    """
    errors: Dict[str, str] = {}
    cleaned_data: Dict[str, Any] = {}

    email = (data.get("email") or "").strip()
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()
    password = data.get("password") or ""
    activo = (data.get("activo") or "").strip().upper()
    rol = (data.get("rol") or "").strip()

    if not email:
        errors["email"] = "El email es requerido."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Formato de email inválido."
    else:
        cleaned_data["email"] = email

    if not nombre:
        errors["nombre"] = "El nombre es requerido."
    else:
        cleaned_data["nombre"] = nombre

    if not apellido:
        errors["apellido"] = "El apellido es requerido."
    else:
        cleaned_data["apellido"] = apellido

    if not editing and not password:
        errors["password"] = "La contraseña es requerida."
    elif password:  # Solo incluir password si se proporciona (importante en edición)
        cleaned_data["password"] = password

    if activo not in ("SI", "NO"):
        errors["activo"] = "Debe ser SI o NO."
    else:
        cleaned_data["activo"] = activo == "SI"  # Convertir a booleano

    if rol not in ("Usuario público", "Editor", "Administrador"):
        errors["rol"] = "Rol inválido."
    else:
        cleaned_data["rol"] = rol

    return cleaned_data, errors
