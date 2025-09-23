from os import environ


class Config(object):
    """Base configuration."""

    DEBUG = True
    TESTING = False
    SECRET_KEY = "secret"


class ProductionConfig(Config):
    """Production configuration."""

    DB_HOST = environ.get("DB_HOST")
    DB_USER = environ.get("DB_USER")
    DB_PASS = environ.get("DB_PASS")
    DB_NAME = environ.get("DB_NAME")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    # Para flask_sqlalchemy_lite
    SQLALCHEMY_ENGINES = {
        "default": "sqlite:///dev.sqlite3"
        # Si querés memoria (se borra al reiniciar):
        # "default": "sqlite+pysqlite:///:memory:"
    }

    # """Development configuration."""

    # DEBUG = True
    # DB_HOST = environ.get("DB_HOST", "localhost")
    # DB_USER = environ.get("DB_USER", "postgres")
    # DB_PASS = environ.get("DB_PASS", "12345")
    # DB_NAME = environ.get("DB_NAME", "grupo37")
    # DB_PORT = environ.get("DB_port", "5432")
    # DB_SCHEME = environ.get("DB_SCHEME", "postgresql")
    # SQLALCHEMY_ENGINES = {
    #     'default': f"{DB_SCHEME}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    # }
    # # TEMPLATES_AUTO_RELOAD = True


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True


config = {
    "development": DevelopmentConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
}
