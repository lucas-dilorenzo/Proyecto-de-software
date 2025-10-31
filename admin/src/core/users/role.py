from sqlalchemy import Column, Integer, String, UniqueConstraint
from src.core.database import db


class Role(db.Model):
    """
    Modelo de rol para la base de datos.

    la base de datos cuenta con los siguientes roles, definidos de forma estática:
    - **PUBLIC**: Usuario público.
    - **EDITOR**: Editor.
    - **MODERATOR**: Moderador de reseñas.
    - **ADMIN**: Administrador.
    - **SYS_ADMIN**: Administrador del sistema (no asignable desde la interfaz).
    """

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("name", name="uq_roles_name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"
