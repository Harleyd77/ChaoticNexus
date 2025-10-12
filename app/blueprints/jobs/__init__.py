"""Jobs blueprint package."""

from flask import Blueprint

bp = Blueprint(
    "jobs",
    __name__,
    url_prefix="/jobs",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402,F401
