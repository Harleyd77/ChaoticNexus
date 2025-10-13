"""Settings repository for application configuration values."""

from __future__ import annotations

from typing import Mapping

from sqlalchemy import select

from ..models import Setting
from .session import session_scope


class SettingsRepository:
    """Encapsulate CRUD operations for key-value settings."""

    def list_settings(self) -> Mapping[str, str]:
        with session_scope() as session:
            rows = session.execute(select(Setting)).scalars().all()
            return {row.name: row.value for row in rows}

    def get_setting(self, name: str) -> Setting | None:
        with session_scope() as session:
            return (
                session.execute(select(Setting).filter(Setting.name == name))
                .scalars()
                .one_or_none()
            )

    def set_setting(self, name: str, value: str) -> Setting:
        with session_scope() as session:
            setting = (
                session.execute(select(Setting).filter(Setting.name == name))
                .scalars()
                .one_or_none()
            )

            if setting is None:
                setting = Setting(name=name, value=value)
                session.add(setting)
            else:
                setting.value = value

            session.flush()
            return setting


settings_repo = SettingsRepository()
