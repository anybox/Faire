import os
from distutils.util import strtobool


class Config:

    DEBUG = False
    JWT_TOKEN_LOCATION = ("headers", "cookies")
    LDAP_BIND_FORMAT = os.getenv("LDAP_BIND_FORMAT")
    LDAP_PROVIDER_URL = os.getenv("LDAP_PROVIDER_URL")
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
    PG_DSN = os.getenv(
        "POSTGRES_DSN", "postgresql://clocky:clocky_password@db:5432/clocky"
    )
    PG_SCHEMA = os.getenv("PG_SCHEMA", "tempsfrac,public")
    SQLALCHEMY_DATABASE_URI = PG_DSN
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": f"-csearch_path={PG_SCHEMA}"}
    }
    SECRET_KEY = os.getenv("SECRET_KEY")
    SERVER_NAME = os.getenv("SERVER_NAME", "clocky.local:5000")
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN", None)
    WTF_CSRF_ENABLED = strtobool(os.getenv("WTF_CSRF_ENABLED", "true"))
    ENV = os.getenv("ENV", "dev")


class DevConfig(Config):

    DEBUG = True
    LOGGING_LEVEL = "DEBUG"
    SECRET_KEY = "secret"
