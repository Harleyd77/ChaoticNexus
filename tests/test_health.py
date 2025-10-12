"""Smoke tests for the Flask application factory."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture()
def app():
    """Instantiate the Flask application in testing mode."""
    app = create_app("testing")
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app) -> FlaskClient:
    """Provide a test client for HTTP assertions."""
    return app.test_client()


def test_healthz(client: FlaskClient) -> None:
    """The health check should respond with a JSON payload."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
