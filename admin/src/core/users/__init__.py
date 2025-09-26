from .user import User, UserRole

__all__ = ["User", "UserRole"]


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()
