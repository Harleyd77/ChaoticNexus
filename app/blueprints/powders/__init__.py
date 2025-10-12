"""Powders blueprint."""

from flask import Blueprint

bp = Blueprint(
    "powders",
    __name__,
    url_prefix="/powders",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
