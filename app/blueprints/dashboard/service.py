"""Service layer for Dashboard."""

from app.services.base import Service


class DashboardService(Service):
    """Domain-specific behaviour for dashboard."""

    def example(self) -> str:
        return "Dashboard placeholder"
