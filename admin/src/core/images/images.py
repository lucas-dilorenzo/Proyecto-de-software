from src.core.database import db
from sqlalchemy.orm import relationship


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"), nullable=False)
    url = db.Column(db.String, nullable=False)
    order = db.Column(db.Integer, nullable=True)
    titulo = db.Column(db.String, nullable=True)
    descripcion = db.Column(db.String, nullable=True)

    site = relationship("Site", back_populates="images")

    def __init__(
        self,
        site_id: int,
        url: str,
        order: int = 0,
        titulo: str = None,
        descripcion: str = None,
    ):
        self.site_id = site_id
        self.url = url
        self.order = order
        self.titulo = titulo
        self.descripcion = descripcion

    def __repr__(self) -> str:
        return f"<Image(id={self.id}, site_id={self.site_id}, url={self.url}, order={self.order}, titulo={self.titulo}, descripcion={self.descripcion})>"
