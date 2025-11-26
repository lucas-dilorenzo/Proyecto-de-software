from src.core.users.user import User, UserRole
from src.core.users.role import Role
from src.core.database import db
from src.core import historicalSites

__all__ = ["User", "UserRole", "Role"]


def get_user_by_email(email):
    """Retrieve a user by their email address."""
    return User.query.filter_by(email=email).first()


def get_user_by_id(user_id):
    """Retrieve a user by their unique ID."""
    return User.query.filter_by(id=user_id).first()


def user_exists(email):
    """Check if a user with the given email exists."""
    return User.query.filter_by(email=email).first() is not None


def create_user(
    email,
    nombre,
    apellido,
    password_hash,
    rol=UserRole.PUBLIC,
    activo=True,
    profile_picture=None,
):
    """Create a new user with the provided details.
    Args:
        email (str): The user's email address.
        nombre (str): The user's first name.
        apellido (str): The user's last name.
        password_hash (str): The hashed password for the user.
        rol (UserRole): The role assigned to the user (default is UserRole.PUBLIC).
        activo (bool): Whether the user is active (default is True).
        profile_picture (str): URL of the user's profile picture (optional, for OAuth).
        Returns:
            User: The newly created user object."""
    user = User(
        email=email,
        nombre=nombre,
        apellido=apellido,
        password_hash=password_hash,
        rol=rol,
        activo=activo,
        profile_picture=profile_picture,
    )
    db.session.add(user)
    db.session.commit()
    return user


def edit_user(user):
    """Edit an existing user's details.
    Args:
        user (User): The user object with updated details.
        Returns:
            User: The updated user object."""
    db.session.commit()
    return user


def validate_email_unique(email, user_id=None):
    """Validate that the email is unique in the database.
    Args:
        email (str): The email address to validate.
        user_id (int, optional): The ID of the user to exclude from the check (useful when updating a user).
        Returns:
            bool: True if the email is unique, False otherwise."""
    query = User.query.filter_by(email=email)
    if user_id:
        query = query.filter(User.id != user_id)
    return query.first() is None


def delete_user(user):
    """Delete a user from the database.
    Args:
        user (User): The user object to delete."""
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
    """Retrieve all roles from the database."""
    return Role.query.all()


def get_role_by_name(name: UserRole):
    """Retrieve a role by its name.
    Args:
        name (UserRole): The name of the role to retrieve.
    Returns:
        Role: The role object if found, None otherwise."""
    return Role.query.filter_by(name=name.value).first()


def get_users_filtered(page=1, per_page=25, email="", activo="", rol="", order="desc"):
    """
    Obtiene usuarios con filtros y paginación

    Args:
        page (int): Número de página actual
        per_page (int): Cantidad de usuarios por página
        email (str): Filtro por email (búsqueda parcial)
        activo (str): Filtro por estado ("SI", "NO" o vacío para todos)
        rol (str): Filtro por rol (debe coincidir con UserRole.value)
        order (str): Ordenamiento por fecha ("asc" o "desc")

    Returns:
        Un objeto paginated con los usuarios filtrados
    """
    # Construir la consulta base
    query = User.query

    # Aplicar filtros
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    if activo in ("SI", "NO"):
        query = query.filter(User.activo == (activo == "SI"))

    if rol:
        role_enum = next((r for r in UserRole if r.value == rol), None)
        if role_enum:
            query = query.filter(User.rol == role_enum)

    # Aplicar ordenamiento
    if order == "asc":
        query = query.order_by(User.created_at.asc())
    else:
        query = query.order_by(User.created_at.desc())

    # Ejecutar la consulta paginada
    return query.paginate(page=page, per_page=per_page, error_out=False)


def marcar_favorito(user: User, site_id: int) -> bool:
    """
    Marca un sitio como favorito para un usuario dado.
    Args:
        user (User): El objeto User que marca el sitio como favorito.
        site_id (int): El ID del sitio a marcar como favorito.
    Returns:
        bool: True si se marcó correctamente, False en caso de error.
    """
    try:
        site = historicalSites.get_site_by_id(site_id)
        if not site:
            return False

        if site not in user.favs:
            user.favs.append(site)
            db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error al marcar favorito: {e}")
        return False


def eliminar_favorito(user: User, site_id: int) -> bool:

    try:
        site = historicalSites.get_site_by_id(site_id)
        # compruebo que el sitio exista
        if not site:
            return False
        # compruebo que esté en favoritos
        if site not in user.favs:
            return False
        # if site in user.favs:
        user.favs.remove(site)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar el favorito: {e}")
        return False


def get_user_favs(user: User):
    """
    Obtiene la lista de sitios favoritos de un usuario.
    Args:
        user (User): El objeto User del cual obtener los favoritos.
    Returns:
        list: Lista de sitios favoritos del usuario.
    """
    favs_sites = [historicalSites.get_site_by_id(site.id) for site in user.favs]
    return favs_sites


def get_jwt_user_by_id(user_id):
    """Retrieve a user by their unique ID for JWT authentication."""
    user = User.query.filter_by(id=user_id).first()
    if user:
        nombre_completo = user.nombre + " " + user.apellido
        user = {
            "nombre": nombre_completo,
            "email": user.email,
            "id": user.id,
            "profile_picture": user.profile_picture,
        }
    return user
