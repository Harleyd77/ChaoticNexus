"""Route smoke tests for legacy parity.

These tests assert basic status codes and redirects for key legacy endpoints.
They do not exercise database writes; JSON shape checks focus on top-level keys
where applicable. Use as guardrails during parity implementation.
"""

from __future__ import annotations

from flask.testing import FlaskClient


def test_root_redirects_to_dashboard(client: FlaskClient) -> None:
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302)


def test_nav_redirects(client: FlaskClient) -> None:
    # Legacy compatibility: /nav should redirect to dashboard
    resp = client.get("/nav", follow_redirects=False)
    assert resp.status_code in (301, 302, 308)


def test_favicon(client: FlaskClient) -> None:
    resp = client.get("/favicon.ico")
    assert resp.status_code in (200, 304, 404)


def test_auth_routes_exist(client: FlaskClient) -> None:
    assert client.get("/auth/login").status_code in (200, 302)
    assert client.get("/auth/logout").status_code in (200, 302, 405)


def test_customer_portal_basic_routes(client: FlaskClient) -> None:
    assert client.get("/customer/").status_code in (200, 302)
    assert client.get("/customer/jobs").status_code in (200, 302)


def test_customers_index(client: FlaskClient) -> None:
    assert client.get("/customers/").status_code in (200, 302)


def test_jobs_index(client: FlaskClient) -> None:
    assert client.get("/jobs/").status_code in (200, 302)


def test_powders_index(client: FlaskClient) -> None:
    assert client.get("/powders/").status_code in (200, 302)


def test_inventory_index(client: FlaskClient) -> None:
    assert client.get("/inventory/").status_code in (200, 302)


def test_intake_routes(client: FlaskClient) -> None:
    assert client.get("/intake/form").status_code in (200, 302)
    assert client.get("/intake/railing").status_code in (200, 302)
