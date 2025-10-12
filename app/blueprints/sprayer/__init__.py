"""Sprayer/batch tracking blueprint."""

from flask import Blueprint

bp = Blueprint(
    "sprayer",
    __name__,
    url_prefix="/sprayer",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
