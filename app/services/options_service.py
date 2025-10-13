"""Options service for editable dropdown lists (jobs, etc.)."""

from __future__ import annotations

import json
from dataclasses import dataclass

from app.repositories import settings_repo

_DEFAULT_JOB_OPTIONS = {
    "category": ["Production", "Architectural", "Industrial", "Custom"],
    "priority": ["Critical", "High", "Normal", "Low"],
    "blast": ["None", "Mechanical", "Chemical"],
    "prep": ["TBD", "Wipe down", "Mask only", "Mask + Hang", "Degrease"],
}


@dataclass
class JobFormOptions:
    category: list[str]
    priority: list[str]
    blast: list[str]
    prep: list[str]


class OptionsService:
    def __init__(self, repository=settings_repo):
        self._repo = repository

    def _get_list(self, key: str, *, default: list[str]) -> list[str]:
        row = self._repo.get_setting(key)
        if not row or not row.value:
            return list(default)
        try:
            parsed = json.loads(row.value)
            if isinstance(parsed, list):
                # Keep only strings and strip whitespace
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
        return list(default)

    def _set_list(self, key: str, items: list[str]) -> None:
        normalized = [str(x).strip() for x in items if str(x).strip()]
        self._repo.set_setting(key, json.dumps(normalized))

    def get_job_form_options(self) -> JobFormOptions:
        return JobFormOptions(
            category=self._get_list(
                "options:jobs:category", default=_DEFAULT_JOB_OPTIONS["category"]
            ),
            priority=self._get_list(
                "options:jobs:priority", default=_DEFAULT_JOB_OPTIONS["priority"]
            ),
            blast=self._get_list("options:jobs:blast", default=_DEFAULT_JOB_OPTIONS["blast"]),
            prep=self._get_list("options:jobs:prep", default=_DEFAULT_JOB_OPTIONS["prep"]),
        )

    def get_job_option_list(self, name: str) -> list[str]:
        if name not in _DEFAULT_JOB_OPTIONS:
            raise ValueError("Unknown options list")
        return self._get_list(f"options:jobs:{name}", default=_DEFAULT_JOB_OPTIONS[name])

    def set_job_option_list(self, name: str, items: list[str]) -> None:
        if name not in _DEFAULT_JOB_OPTIONS:
            raise ValueError("Unknown options list")
        self._set_list(f"options:jobs:{name}", items)


options_service = OptionsService()
