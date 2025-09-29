from src.core.database import db
from sqlalchemy.orm import relationship
from datetime import date


class Site(db.Model):
    __tablename__ = "sites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description_short = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    province = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)  # Could be coordinates
    conservation_status = db.Column(db.String, nullable=True)
    year_declared = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String, nullable=True)
    registration_date = db.Column(db.Date, nullable=True)
    visibility = db.Column(db.Boolean, default=True)

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

