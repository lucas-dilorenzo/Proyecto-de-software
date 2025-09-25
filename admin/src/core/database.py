from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    return db


def reset_db():
    from src.core.historicalSites.site import Site  # noqa: F401
    from core.historicalSites.tags.tag import Tag  # noqa: F401

    print("Resetting database...")
    db.drop_all()
    db.create_all()
    print("Database reset complete.")


class Base(DeclarativeBase):
    pass
