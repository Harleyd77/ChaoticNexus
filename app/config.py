"""Configuration objects for the Chaotic Nexus backend."""

from __future__ import annotations

import os
from functools import cache


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://appuser:apppass@postgres:5432/chaoticnexus",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    WTF_CSRF_ENABLED = True
    # File storage
    UPLOADS_DIR = os.environ.get(
        "UPLOADS_DIR",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "_data", "uploads")),
    )
    # Template reloading (useful during development/staging)
    TEMPLATES_AUTO_RELOAD = os.environ.get("TEMPLATES_AUTO_RELOAD", "false").lower() == "true"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    TEMPLATES_AUTO_RELOAD = True  # Always reload templates in development


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/chaotic_nexus_test",
    )


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


@cache
def get_config(env: str | None) -> type[BaseConfig]:
    """Resolve the config class for the provided environment name."""
    if not env:
        env = os.environ.get("FLASK_ENV", "production")
    env = env.lower()
    return CONFIG_MAP.get(env, ProductionConfig)
