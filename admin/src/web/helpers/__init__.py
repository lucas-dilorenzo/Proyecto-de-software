from enum import Enum
from core.users.user import User, UserRole
from core import users


def is_authenticated(session):
    return session.get("user") is not None


def is_admin(session):
    return session.get("role") == UserRole.ADMIN


def is_editor(session):
    return session.get("role") == UserRole.EDITOR


def is_viewer(session):
    return session.get("role") == UserRole.PUBLIC


def has_role(session, role):
    return session.get("role") == role


def get_user_by_id(id):
    user = users.get_user_by_id(id)
    return user
