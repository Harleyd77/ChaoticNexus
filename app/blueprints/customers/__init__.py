"""Customers blueprint."""

from flask import Blueprint

bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402, F401
