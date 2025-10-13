"""Shared Pytest fixtures for the Chaotic Nexus test suite."""

from __future__ import annotations

import os

import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    os.environ.setdefault(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/chaotic_nexus_test",
    )
    app = create_app("testing")
    app.config.update(TESTING=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["TEST_DATABASE_URL"]
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
