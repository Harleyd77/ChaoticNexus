"""Intake forms blueprint."""

from flask import Blueprint

bp = Blueprint(
    "intake",
    __name__,
    url_prefix="/intake",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
