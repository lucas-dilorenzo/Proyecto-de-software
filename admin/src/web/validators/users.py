import re
from typing import Dict, Tuple

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_user_payload(
    data: Dict, is_update: bool = False
) -> Tuple[bool, Dict[str, str]]:
    """
    data esperado:
      email, nombre, apellido, password(opcional en update), activo("SI"/"NO"), rol(...)
    """
    errors: Dict[str, str] = {}

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

    if not nombre:
        errors["nombre"] = "El nombre es requerido."

    if not apellido:
        errors["apellido"] = "El apellido es requerido."

    if not is_update and not password:
        errors["password"] = "La contraseña es requerida."

    if activo not in ("SI", "NO"):
        errors["activo"] = "Debe ser SI o NO."

    if rol not in ("Usuario público", "Editor", "Administrador"):
        errors["rol"] = "Rol inválido."

    return (len(errors) == 0), errors
