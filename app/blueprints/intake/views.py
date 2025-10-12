"""HTTP endpoints for the Intake blueprint."""

from flask import flash, redirect, render_template, request, url_for

from . import bp


@bp.route("/form", methods=["GET", "POST"])
def intake_form():
    """Production intake form."""
    if request.method == "POST":
        # TODO: Save via repository
        flash("Job intake submitted successfully", "success")
        return redirect(url_for("dashboard.index"))

    return render_template(
        "intake/form.html",
        powders=[],
    )


@bp.route("/railing", methods=["GET", "POST"])
def railing_intake():
    """Railing-specific intake form."""
    if request.method == "POST":
        # TODO: Save via repository
        flash("Railing job submitted successfully", "success")
        return redirect(url_for("dashboard.index"))

    return render_template(
        "intake/railing.html",
        powders=[],
    )
