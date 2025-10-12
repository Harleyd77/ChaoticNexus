"""<Feature> blueprint package."""

from flask import Blueprint

bp = Blueprint(
    "<feature>",
    __name__,
    url_prefix="/<feature>",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402,F401
