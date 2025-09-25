from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    return db


def reset_db():
    from src.core.historicalSites.site import Site  # noqa: F401
    from src.core.users.user import User  # noqa: F401

    print("Resetting database...")
    db.drop_all(bind=db.engine)
    db.create_all(bind=db.engine)
    print("Database reset complete.")


class Base(DeclarativeBase):
    pass
