from dataclasses import dataclass
from flask import render_template

@dataclass
class HTTPError:
    code: int
    message: str
    description: str

def not_found(e):
    error = HTTPError(
        code=404,
        message="Not Found",
        description="No pudimos encontrar el sitio buscado."
    )
    return render_template("error.html", error=error), 404

def unauthorized(e):
    error = HTTPError(
        code=401,
        message="Unauthorized",
        description="Necesitas iniciar sesión para acceder."
    )
    return render_template("error.html", error=error), 401

def generic(e):
    error = HTTPError(
        code=500,
        message="Internal Server Error",
        description="Algo salió mal. Inténtelo de nuevo más tarde."
    )
    return render_template("error.html", error=error), 500
