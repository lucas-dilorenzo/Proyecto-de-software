from src.core.users.user import User, UserRole
from src.core.users.role import Role
from src.core.database import db

__all__ = ["User", "UserRole", "Role"]


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()


def user_exists(email):
    return User.query.filter_by(email=email).first() is not None


def create_user(
    email, nombre, apellido, password_hash, rol=UserRole.PUBLIC, activo=True
):
    user = User(
        email=email,
        nombre=nombre,
        apellido=apellido,
        password_hash=password_hash,
        rol=rol,
        activo=activo,
    )
    db.session.add(user)
    db.session.commit()
    return user


def edit_user(user):
    db.session.commit()
    return user


def validate_email_unique(email, user_id=None):
    query = User.query.filter_by(email=email)
    if user_id:
        query = query.filter(User.id != user_id)
    return query.first() is None


def delete_user(user):
    db.session.delete(user)
    db.session.commit()


def get_users_paginated(page: int = 1, per_page: int = 25, order: str = "asc"):
    """
    Retrieves a paginated list of users from the database.
    Args:
        page (int): The page number to retrieve (default is 1).
        per_page (int): The number of users to display per page (default is 25).
        order (str): The order in which to sort the users by name ('asc' for ascending(default), 'desc' for descending; default is 'asc').
    Returns:
        users: A query containing the paginated list of users and pagination metadata.
    """
    if order == "desc":
        users = User.query.order_by(User.nombre.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        users = User.query.order_by(User.nombre.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    return users


def get_users_paginated_by_id(page: int = 1, per_page: int = 25, order: str = "asc"):
    """
    Retrieves a paginated list of users from the database.
    Args:
        page (int): The page number to retrieve (default is 1).
        per_page (int): The number of users to display per page (default is 25).
        order (str): The order in which to sort the users by id ('asc' for ascending(default), 'desc' for descending; default is 'asc').
    Returns:
        users: A query containing the paginated list of users and pagination metadata.
    """
    if order == "desc":
        users = User.query.order_by(User.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        users = User.query.order_by(User.id.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    return users


def get_all_roles():
    return Role.query.all()


def get_role_by_name(name: UserRole):
    return Role.query.filter_by(name=name.value).first()
