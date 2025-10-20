from src.core.users import user
from geoalchemy2 import Geometry
from sqlalchemy import func
from src.core.database import db
from sqlalchemy.orm import relationship
from datetime import date
from sqlalchemy.ext.hybrid import hybrid_property

sites_tags = db.Table(
    "sites_tags",
    db.Column("site_id", db.Integer, db.ForeignKey("sites.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Site(db.Model):
    __tablename__ = "sites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description_short = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    province = db.Column(db.String, nullable=True)
    location = db.Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    conservation_status = db.Column(db.String, nullable=True)
    year_declared = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String, nullable=True)
    registration_date = db.Column(db.Date, nullable=True)
    visibility = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)

    tags = relationship("Tag", secondary=sites_tags, backref="sites")

    def __init__(
        self,
        name: str,
        description_short: str = None,
        description: str = None,
        city: str = None,
        province: str = None,
        location: str = None,
        conservation_status: str = None,
        year_declared: int = None,
        category: str = None,
        registration_date: date = None,
        visibility: bool = True,
        deleted: bool = False,
    ):
        self.name = name
        self.description_short = description_short
        self.description = description
        self.city = city
        self.province = province
        self.location = location
        self.conservation_status = conservation_status
        self.year_declared = year_declared
        self.category = category
        self.registration_date = registration_date
        self.visibility = visibility
        self.deleted = deleted

    def __repr__(self) -> str:
        return f"<Site(id={self.id}, name={self.name}, city={self.city}, province={self.province})>"

    @hybrid_property
    def latitude(self) -> float:
        if self.location:
            return db.session.scalar(func.ST_Y(self.location))
        return None

    @hybrid_property
    def longitude(self) -> float:
        if self.location:
            return db.session.scalar(func.ST_X(self.location))
        return None

    def to_dict(self):
        """Convierte el objeto Site a un diccionario serializable"""
        # Obtener coordenadas una sola vez para evitar múltiples queries
        lat = self.latitude
        lng = self.longitude

        return {
            "id": self.id,
            "name": self.name,
            "description_short": self.description_short,
            "description": self.description,
            "city": self.city,
            "province": self.province,
            "latitude": lat,
            "longitude": lng,
            "conservation_status": self.conservation_status,
            "year_declared": self.year_declared,
            "category": self.category,
            "registration_date": (
                self.registration_date.isoformat() if self.registration_date else None
            ),
            "visibility": self.visibility,
        }


class SiteLog(db.Model):
    __tabletName__ = "sites_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String, nullable=False)
    timestamp = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    details = db.Column(db.JSON, nullable=True)
    site = relationship("Site", backref="logs")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<SiteLog(id={self.id}, site_id={self.site_id}, user_id={self.user_id}, action={self.action})>"
