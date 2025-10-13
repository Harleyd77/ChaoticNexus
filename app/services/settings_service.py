"""Service layer for administrative application settings."""

from __future__ import annotations

from dataclasses import dataclass

from app.repositories import settings_repo


@dataclass
class SettingsPayload:
    company_name: str


class SettingsService:
    def __init__(self, repository=settings_repo):
        self._repo = repository

    def get_settings(self) -> SettingsPayload:
        data = self._repo.list_settings()
        return SettingsPayload(
            company_name=data.get("company_name", "Victoria Powder Coating"),
        )

    def update_settings(self, *, company_name: str | None) -> SettingsPayload:
        if company_name is not None:
            cleaned = company_name.strip()
            if not cleaned:
                raise ValueError("Company name cannot be empty")
            self._repo.set_setting("company_name", cleaned)

        return self.get_settings()


settings_service = SettingsService()
