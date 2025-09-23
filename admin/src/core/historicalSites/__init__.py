from src.core.historicalSites.site import Site  # noqa: F401
from src.core.database import db


def list_all():
    return db.session.query(Site).all()


def get_by_id(site_id: int):
    return db.session.query(Site).filter(Site.id == site_id).first()


def get_by_name(name: str):
    return db.session.query(Site).filter(Site.name == name).first()
