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

    id: Mapped[int] = Column(primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(20), nullable=False)
    roles: Mapped[list[Role]] = relationship(secondary=role_permissions)

    def __repr__(self):
        return f"<Permission {self.name}>"


class UserPermission(str, Enum):
    """
    Enum de permisos posibles.
    """

    USER_CREATE = "user_create"
    USER_LIST = "user_list"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ROLE = "user_role"
    USER_BLOCK = "user_block"
    SITE_CREATE = "site_create"
    SITE_LIST = "site_list"
    SITE_UPDATE = "site_update"
    SITE_DELETE = "site_delete"
    SITE_TAGS = "site_tags"
    SITE_EXPORT = "site_export"
    SITE_HISTORY = "site_history"
    FLAGS = "flags"
