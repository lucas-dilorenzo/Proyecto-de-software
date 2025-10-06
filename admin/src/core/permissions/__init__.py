from sqlalchemy import select
from src.core.users.user import UserRole
from src.core.permissions.permission import Permission, UserPermission, Role
from src.core.database import db


def check_permission(user_role: UserRole, perm: UserPermission):
    print(f"Role: {user_role.value}", end="; ")
    if user_role == UserRole.SYS_ADMIN:
        return True
    allowed_roles = db.session.execute(
        select(Role.name).join(Permission.roles).where(Permission.name == perm.value[0])
    ).all()
    allowed_roles = list(map(lambda r: r[0], allowed_roles))
    print(f"Allowed roles: {allowed_roles}")
    return user_role.name in allowed_roles
