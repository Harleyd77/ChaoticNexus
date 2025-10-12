"""Smoke tests for jobs blueprint."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture()
def client() -> FlaskClient:
    app = create_app("testing")
    return app.test_client()


def test_jobs_index(client: FlaskClient) -> None:
    """Jobs index should render successfully."""
    response = client.get("/jobs/")
    assert response.status_code == 200
    assert b"Jobs" in response.data


def test_jobs_kanban(client: FlaskClient) -> None:
    """Jobs kanban should render successfully."""
    response = client.get("/jobs/kanban")
    assert response.status_code == 200
    assert b"Jobs Kanban" in response.data


def test_job_detail(client: FlaskClient) -> None:
    """Job detail should render for sample placeholder job."""
    response = client.get("/jobs/1042/")
    assert response.status_code == 200
    assert b"Job #1042" in response.data


def test_job_edit(client: FlaskClient) -> None:
    """Job edit form should render for placeholder job."""
    response = client.get("/jobs/1042/edit")
    assert response.status_code == 200
    assert b"Edit Job #1042" in response.data
