"""Service-layer tests for application settings."""

from __future__ import annotations

import pytest

from app.services.settings_service import SettingsService


@pytest.fixture()
def service(app):
    with app.app_context():
        yield SettingsService()


def test_get_settings_returns_defaults(service):
    payload = service.get_settings()

    assert payload.company_name == "Victoria Powder Coating"


def test_update_settings_persists_value(service):
    updated = service.update_settings(company_name="Chaotic Nexus Labs")

    assert updated.company_name == "Chaotic Nexus Labs"


def test_update_settings_rejects_empty_company_name(service):
    with pytest.raises(ValueError):
        service.update_settings(company_name="   ")
