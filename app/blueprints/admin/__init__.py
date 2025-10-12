"""Admin blueprint."""

from flask import Blueprint

bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
