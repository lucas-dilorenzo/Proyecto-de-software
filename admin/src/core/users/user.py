"""
Definición del modelo User y el enum UserRole para la gestión de usuarios en la aplicación.
Incluye roles, restricciones y campos relevantes para autenticación y administración.
"""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
# from core.database import db
from src.core.database import db
import enum


class UserRole(str, enum.Enum):
    """
    Enum de roles posibles para los usuarios del sistema.
    """

    PUBLIC = "Usuario público"
    EDITOR = "Editor"
    ADMIN = "Administrador"


class User(db.Model):
    """
    Modelo de usuario para la base de datos.
    Incluye información personal, credenciales, estado y rol.
    """

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(String(255), nullable=False)
    nombre = db.Column(String(120), nullable=False)
    apellido = db.Column(String(120), nullable=False)
    password_hash = db.Column(String(255), nullable=False)
    activo = db.Column(Boolean, default=True, nullable=False)
    rol = db.Column(Enum(UserRole), nullable=False, default=UserRole.PUBLIC)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.email} ({self.rol})>"
