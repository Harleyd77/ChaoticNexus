"""Repository layer package."""

from __future__ import annotations

from .customers import CustomerRepository, customer_repo
from .inventory import InventoryRepository, inventory_repo
from .jobs import JobRepository, job_repo
from .powders import PowderRepository, powder_repo
from .session import get_session, session_scope
from .settings import SettingsRepository, settings_repo

__all__ = [
    "CustomerRepository",
    "InventoryRepository",
    "JobRepository",
    "PowderRepository",
    "SettingsRepository",
    "customer_repo",
    "inventory_repo",
    "job_repo",
    "powder_repo",
    "settings_repo",
    "get_session",
    "session_scope",
]
