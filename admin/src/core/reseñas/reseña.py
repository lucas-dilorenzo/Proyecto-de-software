from src.core.database import db
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from src.core.reseñas.estadoReseña import estadoReseña
from datetime import datetime, timezone


class Reseña(db.Model):
    __tablename__ = "reseñas"

    # Para asegurar que un usuario solo pueda dejar una reseña por sitio
    __table_args__ = (
        UniqueConstraint("user_id", "site_id", name="uq_user_site_reseña"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    calificacion = db.Column(db.Integer, nullable=False)
    contenido = db.Column(db.String, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", backref="reseñas")
    site_id = db.Column(
        db.Integer, db.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    site = relationship("Site", backref="reseñas")
    estado = db.Column(db.String, nullable=False, default=estadoReseña.PENDIENTE.code)
    motivo_rechazo = db.Column(db.String(200), nullable=True)
    fecha_creacion = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return (
            f"<Reseña(id={self.id}, "
            f"calificacion={self.calificacion}, "
            f"contenido='{self.contenido[:50]}...', "
            f"user_id={self.user_id}, "
            f"site_id={self.site_id}, "
            f"estado='{self.estado}', "
            f"motivo_rechazo='{self.motivo_rechazo}', "
            f"fecha_creacion={self.fecha_creacion})>"
        )
