from src.core.users.user import UserRole
from src.core.permissions.permission import Permission, UserPermission, Role
from src.core.database import db


def get_permission_roles(perm: UserPermission) -> Role:
    permission = db.session.query(Permission).filter_by(name=perm.value).first()
    if permission is not None:
        return permission.roles


def check_permission(user_role: UserRole, perm: UserPermission):
    roles = db.session.query(Role).filter(Role.id in get_permission_roles(perm)).all()
    return user_role in roles
