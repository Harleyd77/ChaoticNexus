"""Service-level tests for inventory dashboard logic."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.extensions import db
from app.models import Powder
from app.services.inventory_service import InventoryService


@pytest.fixture()
def service(app):
    with app.app_context():
        yield InventoryService()


@pytest.fixture()
def sample_powders(app):
    with app.app_context():
        powder_a = Powder(powder_color="Ocean Blue", on_hand_kg=Decimal("8.5"))
        powder_b = Powder(powder_color="Sunset Orange", on_hand_kg=Decimal("2.0"))
        powder_c = Powder(powder_color="Night Sky", on_hand_kg=Decimal("0"))
        db.session.add_all([powder_a, powder_b, powder_c])
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Powder).delete()
        db.session.commit()


def test_powders_dashboard_buckets(app, service, sample_powders):
    with app.app_context():
        powders, summary = service.powders_dashboard()

    assert summary.total_powders == 3
    assert summary.in_stock == 1
    assert summary.low_stock == 1
    assert summary.out_of_stock == 1

    names = {powder.powder_color for powder in powders}
    assert names == {"Ocean Blue", "Sunset Orange", "Night Sky"}


def test_recent_logs_empty(app, service, sample_powders):
    with app.app_context():
        powder = db.session.query(Powder).filter_by(powder_color="Ocean Blue").first()
        assert service.recent_logs(powder.id) == []
