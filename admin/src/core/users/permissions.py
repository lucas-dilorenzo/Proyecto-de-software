from core.database import Base
from core.users import UserRole
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    roles: Mapped[list["UserRole"]] = relationship(secondary=role_permissions)

    def __repr__(self) -> str:
        return f"<Permission(name={self.name}, description={self.description}, roles={[role.name for role in self.roles]})>"
