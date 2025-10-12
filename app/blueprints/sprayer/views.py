"""HTTP endpoints for the Sprayer blueprint."""

from flask import render_template

from . import bp


@bp.route("/hitlist")
def hitlist():
    """Sprayer hit list page."""
    # TODO: Load from repository once implemented
    return render_template(
        "sprayer/hitlist.html",
        jobs=[],
    )


@bp.route("/batches")
def batches():
    """Spray batches page."""
    # TODO: Load from repository once implemented
    return render_template(
        "sprayer/batches.html",
        batches=[],
    )
