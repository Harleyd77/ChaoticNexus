"""Base service abstractions."""

from __future__ import annotations

from typing import Protocol


class Service(Protocol):
    """Marker protocol for application services."""

    def example(self) -> str:
        """Return a placeholder value (override in concrete services)."""
        raise NotImplementedError
