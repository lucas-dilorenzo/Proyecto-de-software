from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException, NotFound
from .exceptions import APIException, ServerError, NotFoundError

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(APIException)
def handle_api_exception(error):
    """Maneja excepciones custom de API"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api_bp.errorhandler(404)
def handle_not_found(error):
    """Maneja 404 en endpoints de API (devuelve JSON en lugar de HTML)"""
    response = jsonify(
        {"error": {"code": "not_found", "message": "Resource not found"}}
    )
    response.status_code = 404
    return response


@api_bp.errorhandler(HTTPException)
def handle_http_exception(error):
    """Maneja excepciones HTTP de Werkzeug"""
    response = jsonify(
        {
            "error": {
                "code": error.name.lower().replace(" ", "_"),
                "message": error.description,
            }
        }
    )
    response.status_code = error.code
    return response


@api_bp.errorhandler(Exception)
def handle_unexpected_exception(error):
    """Maneja errores inesperados (500)"""
    # Log del error real (no exponerlo al cliente)
    import traceback

    print(f"❌ Unexpected error: {error}")
    traceback.print_exc()

    # Respuesta genérica al cliente
    server_error = ServerError()
    response = jsonify(server_error.to_dict())
    response.status_code = 500
    return response


# Importar rutas después de definir error handlers
from . import sites
from . import authenticate
