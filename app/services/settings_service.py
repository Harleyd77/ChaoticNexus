"""Service layer for administrative application settings."""

from __future__ import annotations

from dataclasses import dataclass

from app.repositories import settings_repo


@dataclass
class SettingsPayload:
    company_name: str
    brand_primary: str
    brand_accent: str
    logo_url: str | None


class SettingsService:
    def __init__(self, repository=settings_repo):
        self._repo = repository

    def get_settings(self) -> SettingsPayload:
        data = self._repo.list_settings()
        return SettingsPayload(
            company_name=data.get("company_name", "Victoria Powder Coating"),
            brand_primary=data.get("brand_primary", "#10b981"),
            brand_accent=data.get("brand_accent", "#06b6d4"),
            logo_url=data.get("logo_url"),
        )

    def update_settings(
        self,
        *,
        company_name: str | None = None,
        brand_primary: str | None = None,
        brand_accent: str | None = None,
        logo_url: str | None = None,
    ) -> SettingsPayload:
        if company_name is not None:
            cleaned = company_name.strip()
            if not cleaned:
                raise ValueError("Company name cannot be empty")
            self._repo.set_setting("company_name", cleaned)
        if brand_primary is not None:
            self._repo.set_setting("brand_primary", brand_primary.strip())
        if brand_accent is not None:
            self._repo.set_setting("brand_accent", brand_accent.strip())
        if logo_url is not None:
            self._repo.set_setting("logo_url", logo_url.strip())

        return self.get_settings()


settings_service = SettingsService()
