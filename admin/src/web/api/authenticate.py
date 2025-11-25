from flask import (
    request,
    make_response,
)
from werkzeug.security import check_password_hash
from src.core import users
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
from flask import jsonify
from . import api_bp


@api_bp.post("/auth/login_jwt")
def login_jwt():
    """Handles JWT-based user login.
    Expects JSON with "email" and "password".
    Returns:
        201 with JWT cookies on success, 401 on failure.
    """
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    user = users.get_user_by_email(email)

    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        response = make_response(
            jsonify({"access_token": access_token, "user_id": user.id}), 201
        )
        set_access_cookies(response, access_token)
        return response
    else:
        return jsonify(message="Unauthorized"), 401


@api_bp.get("/auth/logout_jwt")
@jwt_required()
def logout_jwt():
    """Handles JWT-based user logout.
    Returns:
        200 on success."""
    response = jsonify()
    unset_jwt_cookies(response)
    return response, 200


@api_bp.get("/auth/user_jwt")
@jwt_required()
def user_jwt():
    """Retrieves the authenticated user via JWT.
    Returns:
        200 with user data on success."""
    try:
        current_user = get_jwt_identity()
        user = users.get_jwt_user_by_id(current_user)
        response = jsonify(user)
        return response, 200
    except Exception as e:
        response = {
            "error": {
                "code": "invalid_credentials",
                "message": "Credenciales inválidas.",
            }
        }
        return jsonify(response), 500
