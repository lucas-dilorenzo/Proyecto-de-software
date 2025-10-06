from enum import Enum
from src.core.users.role import Role
from src.core.users.user import UserRole
from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped
from src.core.database import db

role_permissions = db.Table(
    "role_permissions",
    db.metadata,
    Column("role_id", ForeignKey("roles.id"), nullable=False),
    Column("permission_id", ForeignKey("permissions.id"), nullable=False),
)


class Permission(db.Model):
    """
    Modelo de permiso para la base de datos.

    A continuación, se listan los permisos disponibles en la base de datos y los roles que los poseen:

    Nota:
    * Todas las funciones autorizadas para un Editor también lo están para un Administrador.
    * Todas las funciones autorizadas para un Administrador también lo están para el SysAdmin.

    | Función        | Descripción                                    | Rol             |
    |:-------------- |:---------------------------------------------- |:--------------- |
    | `user_create`  | Crear usuarios                                 | Administrador   |
    | `user_list`    | Listar y ver usuarios                          | Administrador   |
    | `user_update`  | Modificar usuarios                             | Administrador   |
    | `user_delete`  | Eliminar usuarios                              | Administrador   |
    | `user_role`    | Cambiar el rol de un usuario                   | Administrador   |
    | `user_block`   | Bloquear y desbloquear usuarios                | Administrador   |
    | `site_create`  | Crear sitios                                   | Editor          |
    | `site_list`    | Listar y ver sitios                            | Usuario público |
    | `site_update`  | Modificar sitios                               | Editor          |
    | `site_delete`  | Eliminar sitios                                | Administrador   |
    | `site_tags`    | Gestionar etiquetas de sitio                   | Editor          |
    | `site_export`  | Exportar información de sitios en formato CSV  | Administrador   |
    | `site_history` | Ver el historial de modificaciones de un sitio | Editor          |
    | `flags`        | Ver y modificar las feature flags              | SysAdmin        |
    """

    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("name", name="uq_permissions_name"),)

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )  # Agregar db.Integer aquí
    name = db.Column(db.String(20), nullable=False)  # Usar db.String en vez de String
    roles = db.relationship("Role", secondary=role_permissions, backref="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"


class UserPermission(tuple[str, list[UserRole]], Enum):
    """
    Enum de permisos posibles.
    """

    USER_CREATE = ("user_create", [UserRole.ADMIN])
    USER_LIST = ("user_list", [UserRole.ADMIN])
    USER_UPDATE = ("user_update", [UserRole.ADMIN])
    USER_DELETE = ("user_delete", [UserRole.ADMIN])
    USER_ROLE = ("user_role", [UserRole.ADMIN])
    USER_BLOCK = ("user_block", [UserRole.ADMIN])
    SITE_CREATE = ("site_create", [UserRole.EDITOR, UserRole.ADMIN])
    SITE_LIST = ("site_list", [UserRole.PUBLIC, UserRole.EDITOR, UserRole.ADMIN])
    SITE_UPDATE = ("site_update", [UserRole.EDITOR, UserRole.ADMIN])
    SITE_DELETE = ("site_delete", [UserRole.ADMIN])
    SITE_TAGS = ("site_tags", [UserRole.EDITOR, UserRole.ADMIN])
    SITE_EXPORT = ("site_export", [UserRole.ADMIN])
    SITE_HISTORY = ("site_history", [UserRole.EDITOR, UserRole.ADMIN])
    FLAGS = ("flags", [UserRole.SYS_ADMIN])
