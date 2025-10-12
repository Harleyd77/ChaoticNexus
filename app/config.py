"""Configuration objects for the Chaotic Nexus backend."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Type


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@db:5432/chaotic_nexus",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/chaotic_nexus_test",
    )


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP: dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


@lru_cache(maxsize=None)
def get_config(env: str | None) -> Type[BaseConfig]:
    """Resolve the config class for the provided environment name."""
    if not env:
        env = os.environ.get("FLASK_ENV", "production")
    env = env.lower()
    return CONFIG_MAP.get(env, ProductionConfig)
