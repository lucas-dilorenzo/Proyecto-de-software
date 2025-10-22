from enum import Enum

from flask import redirect, session, url_for
from src.core.users.user import UserRole
from src.core import users
from functools import wraps


def is_authenticated(session):
    """Check if the user is authenticated based on the session."""
    return session.get("user") is not None


def is_admin(session):
    """Check if the user has an admin role based on the session."""
    return session.get("role") == UserRole.ADMIN


def is_editor(session):
    """Check if the user has an editor role based on the session."""
    return session.get("role") == UserRole.EDITOR


def is_viewer(session):
    """Check if the user has a viewer role based on the session."""
    return session.get("role") == UserRole.PUBLIC


def has_role(session, role):
    """Check if the user has the specified role based on the session."""
    return session.get("role") == role


def get_user_by_id(id):
    """Retrieve a user by their unique ID."""
    user = users.get_user_by_id(id)
    return user


def login_required(f):
    """Decorator to ensure the user is authenticated before accessing a route."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated(session):
            print("User not authenticated, redirecting to login.")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function
