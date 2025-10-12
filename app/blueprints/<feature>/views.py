"""HTTP endpoints for the <Feature> blueprint."""

from flask import render_template

from . import bp


@bp.get("/")
def index():
    """Landing page for <feature>."""
    return render_template("<feature>/index.html")
