"""Print templates blueprint."""

from flask import Blueprint

bp = Blueprint(
    "print_templates",
    __name__,
    url_prefix="/api/print-templates",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
