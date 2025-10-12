"""Custom Flask CLI commands."""

from __future__ import annotations

import click
from flask import current_app

__all__ = ["hello"]


@click.command("hello")
def hello() -> None:
    """Example CLI command."""
    current_app.logger.info("Hello from Chaotic Nexus!")
