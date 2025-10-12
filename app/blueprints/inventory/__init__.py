"""Inventory blueprint."""

from flask import Blueprint

bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/inventory",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
