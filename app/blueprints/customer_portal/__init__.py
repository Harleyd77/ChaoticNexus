"""Customer portal blueprint."""

from flask import Blueprint

bp = Blueprint(
    "customer_portal",
    __name__,
    url_prefix="/customer",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
