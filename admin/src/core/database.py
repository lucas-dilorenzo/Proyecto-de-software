from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    return db


def reset_db():
    from src.core.historicalSites.site import Site  # noqa: F401
    from src.core.historicalSites.tag import Tag  # noqa: F401

    print("Resetting database...")
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("Database reset complete.")


class Base(DeclarativeBase):
    pass
