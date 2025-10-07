from src.core.users import user
from geoalchemy2 import Geometry
from src.core.database import db
from sqlalchemy.orm import relationship
from datetime import date

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

    def __repr__(self) -> str:
        return f"<Site(id={self.id}, name={self.name}, city={self.city}, province={self.province})>"
    
class SiteLog(db.Model):
    __tabletName__= "sites_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id") , nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    details = db.Column(db.JSON, nullable=True) 
    site = relationship("Site", backref="logs")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<SiteLog(id={self.id}, site_id={self.site_id}, user_id={self.user_id}, action={self.action})>"





