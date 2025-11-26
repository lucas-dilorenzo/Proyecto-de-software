from datetime import timedelta
from os import environ


class Config(object):
    """Base configuration."""

    DEBUG = True
    TESTING = False
    SECRET_KEY = "secret"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)


class ProductionConfig(Config):
    """Production configuration."""

    DB_HOST = environ.get("DB_HOST")
    DB_USER = environ.get("DB_USER")
    DB_PASS = environ.get("DB_PASS")
    DB_NAME = environ.get("DB_NAME")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")

    MINIO_ENDPOINT = environ.get("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = False
    MINIO_BUCKET_NAME = environ.get("MINIO_BUCKET_NAME", "grupo37")

    PUBLIC_FRONTEND_URL = environ.get(
        "PUBLIC_FRONTEND_URL", "https://grupo37.proyecto2025.linti.unlp.edu.ar/"
    )

    GOOGLE_CLIENT_ID = "tu-client-id"
    GOOGLE_CLIENT_SECRET = "tu-client-secret"


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True

    # Primero: soportar DATABASE_URL 12-factor
    # Ej: export DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname"
    DATABASE_URL = environ.get("DATABASE_URL")

    # Si no hay DATABASE_URL, leemos variables individuales (compatibilidad con development branch)
    DB_HOST = environ.get("DB_HOST", "localhost")
    DB_USER = environ.get("DB_USER", "admin")
    DB_PASS = environ.get("DB_PASS", "12345")
    DB_NAME = environ.get("DB_NAME", "grupo37")
    DB_PORT = environ.get("DB_PORT", "5432")
    DB_SCHEME = environ.get("DB_SCHEME", "postgresql")
    SQLALCHEMY_DATABASE_URI = (
        f"{DB_SCHEME}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    MINIO_ENDPOINT = environ.get("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY", "admin")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY", "adminpassword")
    MINIO_SECURE = False
    MINIO_BUCKET_NAME = environ.get("MINIO_BUCKET_NAME", "grupo37")

    GOOGLE_CLIENT_ID = (
        "GOOGLE_CLIENT_ID_REMOVED"
    )
    GOOGLE_CLIENT_SECRET = "GOOGLE_CLIENT_SECRET_REMOVED"

    # Determinamos la URI final: si hay DATABASE_URL la usamos; si no, construimos desde las partes;
    # si ninguna de las dos está (caso equipo que quiere sqlite), caemos a SQLite local.
    if DATABASE_URL:
        sqlalchemy_uri = DATABASE_URL
    else:
        # Construimos URI solo si DB_SCHEME está definido (por si acaso)
        if DB_SCHEME:
            sqlalchemy_uri = (
                f"{DB_SCHEME}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            )
        else:
            sqlalchemy_uri = None

    # flask_sqlalchemy_lite espera un dict SQLALCHEMY_ENGINES
    if sqlalchemy_uri:
        SQLALCHEMY_ENGINES = {"default": sqlalchemy_uri}
    else:
        # Fallback por defecto: sqlite local (archivo dev.sqlite3)
        SQLALCHEMY_ENGINES = {"default": "sqlite:///dev.sqlite3"}
        # alternativa memoria:
        # SQLALCHEMY_ENGINES = {"default": "sqlite+pysqlite:///:memory:"}


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True


config = {
    "development": DevelopmentConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
}
