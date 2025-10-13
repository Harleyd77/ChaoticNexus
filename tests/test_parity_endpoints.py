from __future__ import annotations

from flask.testing import FlaskClient


def test_legacy_intake_redirects(client: FlaskClient) -> None:
    assert client.get("/intake_form", follow_redirects=False).status_code in (301, 302, 308)
    assert client.get("/railing_intake", follow_redirects=False).status_code in (301, 302, 308)


def test_powders_json_endpoints(client: FlaskClient) -> None:
    assert client.get("/powders/families.json").status_code in (200, 204)
    assert client.get("/powders/colors_full.json").status_code in (200, 204)
    assert client.get("/powders/by_color.json?q=RAL").status_code in (200, 204)


def test_inventory_json_endpoints(client: FlaskClient) -> None:
    assert client.get("/inventory/api/powders").status_code == 200
    assert client.get("/inventory/api/reorder").status_code == 200


def test_print_templates_api(client: FlaskClient) -> None:
    assert client.get("/api/print-templates/work-order").status_code in (200, 204)
    assert client.get("/api/print-templates/work-order/all").status_code in (200, 204)


def test_sprayer_json_endpoints(client: FlaskClient) -> None:
    assert client.get("/sprayer/candidates.json").status_code == 200
    assert client.get("/sprayer/hitlist.json").status_code == 200
