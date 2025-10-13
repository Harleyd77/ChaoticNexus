"""HTTP endpoints for the Dashboard blueprint."""

from flask import redirect, render_template, session, url_for

from . import bp


@bp.get("/")
def index():
    """Landing page for dashboard."""
    # TODO: replace mocked permissions with real data once the auth layer is wired up.
    default_perms = {
        "see_intake": True,
        "see_railing": True,
        "see_job_screen": True,
        "see_jobs": True,
        "see_archived": True,
        "see_powders": True,
        "see_customers": True,
    }
    context = {
        "perms": session.get("perms", default_perms),
        "is_admin": session.get("is_admin", False),
        "me_username": session.get("me_username"),
    }
    return render_template("dashboard/index.html", **context)


@bp.get("/../nav")
def legacy_nav_redirect():
    """Legacy `/nav` path should redirect to dashboard.

    We intentionally route this within the dashboard blueprint to avoid a new
    top-level blueprint solely for a legacy alias.
    """
    return redirect(url_for("dashboard.index"), code=308)
