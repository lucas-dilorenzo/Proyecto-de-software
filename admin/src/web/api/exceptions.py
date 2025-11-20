from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIException(Exception):
    status_code = 400
    code = "api_error"
    message = "An error occurred"
    details = None

    def __init__(self, message=None, details=None, status_code=None):
        super().__init__()
        if message:
            self.message = message
        if details:
            self.details = details
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        error = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            error["details"] = self.details
        return {"error": error}


class ValidationError(APIException):
    status_code = 400
    code = "invalid_query"
    message = "Parameter validation failed"


class NotFoundError(APIException):
    status_code = 404
    code = "not_found"
    message = "Resource not found"


class UnauthorizedError(APIException):
    status_code = 401
    code = "unauthorized"
    message = "Authentication required"


class ForbiddenError(APIException):
    status_code = 403
    code = "forbidden"
    message = "Insufficient permissions"


class ServerError(APIException):
    status_code = 500
    code = "server_error"
    message = "An unexpected error occurred"
