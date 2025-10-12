"""Dashboard blueprint package."""

from flask import Blueprint

bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402,F401
