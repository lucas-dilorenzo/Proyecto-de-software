"""
Definición del modelo User y el enum UserRole para la gestión de usuarios en la aplicación.
Incluye roles, restricciones y campos relevantes para autenticación y administración.
"""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base
import enum


class UserRole(str, enum.Enum):
    """
    Enum de roles posibles para los usuarios del sistema.
    """

    PUBLIC = "Usuario público"
    EDITOR = "Editor"
    ADMIN = "Administrador"


class User(Base):
    """
    Modelo de usuario para la base de datos.
    Incluye información personal, credenciales, estado y rol.
    """

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    apellido: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rol: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.PUBLIC
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<User {self.email} ({self.rol})>"
