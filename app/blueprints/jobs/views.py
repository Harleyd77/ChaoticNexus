"""HTTP endpoints for Jobs blueprint."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

from flask import render_template

from . import bp

_KANBAN_COLUMNS: list[dict[str, str | bool]] = [
    {"key": "intake", "label": "Intake Queue", "timer": False},
    {"key": "prep", "label": "Prep & Masking", "timer": True},
    {"key": "coating", "label": "Coating Booth", "timer": True},
    {"key": "qa", "label": "Quality Review", "timer": False},
    {"key": "completed", "label": "Ready / Completed", "timer": False},
]

_FORM_OPTIONS = {
    "category": ["Production", "Architectural", "Industrial", "Custom"],
    "priority": ["Critical", "High", "Normal", "Low"],
    "blast": ["None", "Mechanical", "Chemical"],
    "prep": ["TBD", "Wipe down", "Mask only", "Mask + Hang", "Degrease"],
}

_DEPARTMENTS = [
    ("intake", "Intake Queue"),
    ("prep", "Prep & Masking"),
    ("coating", "Coating Booth"),
    ("qa", "Quality Review"),
    ("completed", "Ready / Completed"),
    ("shipping", "Shipping / Pickup"),
]


def _sample_jobs() -> list[dict[str, str | int | bool]]:
    """Provide placeholder job data until repositories are implemented."""
    today = date.today()
    return [
        {
            "id": 1042,
            "customer": "Evergreen Railings",
            "reference": "PO-4587",
            "status": "Prep",
            "status_slug": "prep",
            "department": "prep",
            "due": (today + timedelta(days=2)).isoformat(),
            "due_pretty": (today + timedelta(days=2)).strftime("%b %d"),
            "coating": "Tiger Drylac RAL 9005",
            "notes": "Railings + gate hardware. Prep complete, waiting on powder.",
            "has_photos": True,
            "next_step": "Assign to batch",
            "priority": "High",
            "color": "RAL 9005",
            "description": "Exterior railings (200 ft). Request matte finish.",
            "at_risk": False,
            "is_running": True,
            "archived": False,
            "completed_at": None,
            "created_at": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "date_in": (today - timedelta(days=5)).isoformat(),
            "contact_name": "Jamie Collins",
            "phone": "250-555-0198",
            "email": "projects@evergreenrailings.ca",
            "po": "PO-4587",
            "type": "Production",
            "blast": "Mechanical",
            "prep": "Mask + Hang",
        },
        {
            "id": 1038,
            "customer": "Island Builders",
            "reference": "WO-7934",
            "status": "Coating",
            "status_slug": "coating",
            "department": "coating",
            "due": (today + timedelta(days=1)).isoformat(),
            "due_pretty": (today + timedelta(days=1)).strftime("%b %d"),
            "coating": "Prismatic Illusion Sparkle",
            "notes": "Customer requested extra gloss inspection.",
            "has_photos": False,
            "next_step": "QA inspection",
            "priority": "Normal",
            "color": "Illusion Sparkle",
            "description": "Aluminum panels – ensure even coverage on edges.",
            "at_risk": True,
            "is_running": True,
            "archived": False,
            "completed_at": None,
            "created_at": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "date_in": (today - timedelta(days=4)).isoformat(),
            "contact_name": "Alex Rivera",
            "phone": "250-555-0112",
            "email": "alex@islandbuilders.com",
            "po": "WO-7934",
            "type": "Architectural",
            "blast": "Chemical",
            "prep": "Degrease",
        },
        {
            "id": 1033,
            "customer": "Van Isle Fabrication",
            "reference": "PO-4411",
            "status": "Completed",
            "status_slug": "completed",
            "department": "completed",
            "due": today.isoformat(),
            "due_pretty": today.strftime("%b %d"),
            "coating": "Cardinal BK09",
            "notes": "Ready for pickup. Invoice sent.",
            "has_photos": True,
            "next_step": "Await pickup",
            "priority": None,
            "color": "BK09",
            "description": "",
            "at_risk": False,
            "is_running": False,
            "archived": False,
            "completed_at": today.strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
            "date_in": (today - timedelta(days=12)).isoformat(),
            "contact_name": "Morgan Hill",
            "phone": "250-555-0144",
            "email": "orders@vanislefab.ca",
            "po": "PO-4411",
            "type": "Industrial",
            "blast": "None",
            "prep": "Wipe down",
        },
        {
            "id": 1027,
            "customer": "Pacific Custom Metal",
            "reference": "PO-4374",
            "status": "QA Review",
            "status_slug": "qa",
            "department": "qa",
            "due": (today + timedelta(days=3)).isoformat(),
            "due_pretty": (today + timedelta(days=3)).strftime("%b %d"),
            "coating": "Sherwin Illusion Cherry",
            "notes": "QA verifying gloss level meets spec.",
            "has_photos": False,
            "next_step": "QA sign-off",
            "priority": "High",
            "color": "Illusion Cherry",
            "description": "Batch of bike racks – check weld coverage.",
            "at_risk": False,
            "is_running": False,
            "archived": False,
            "completed_at": None,
            "created_at": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            "date_in": (today - timedelta(days=6)).isoformat(),
            "contact_name": "Taylor Ng",
            "phone": "250-555-0176",
            "email": "taylor@pcmmetal.com",
            "po": "PO-4374",
            "type": "Production",
            "blast": "Mechanical",
            "prep": "Mask only",
        },
        {
            "id": 1021,
            "customer": "Cascade Fixtures",
            "reference": "PO-4311",
            "status": "Awaiting Intake",
            "status_slug": "intake",
            "department": "intake",
            "due": (today + timedelta(days=5)).isoformat(),
            "due_pretty": (today + timedelta(days=5)).strftime("%b %d"),
            "coating": "Tiger Bengal Silver",
            "notes": "Customer dropping parts tomorrow morning.",
            "has_photos": False,
            "next_step": "Verify materials on arrival",
            "priority": None,
            "color": None,
            "description": "Fixture arms, 50 units. Use hanging rack C.",
            "at_risk": False,
            "is_running": False,
            "archived": False,
            "completed_at": None,
            "created_at": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "date_in": None,
            "contact_name": "Chris Porter",
            "phone": "250-555-0192",
            "email": "chris@cascadefixtures.com",
            "po": "PO-4311",
            "type": "Architectural",
            "blast": "None",
            "prep": "TBD",
        },
    ]


def _group_jobs_by_department(
    jobs: Iterable[dict[str, str | int | bool]],
) -> dict[str, list[dict[str, str | int | bool]]]:
    grouped: dict[str, list[dict[str, str | int | bool]]] = {
        col["key"]: [] for col in _KANBAN_COLUMNS
    }
    for job in jobs:
        department = str(job.get("department") or "intake")
        grouped.setdefault(department, []).append(job)
    return grouped


@bp.get("/")
def index():
    """Render the jobs index view with placeholder data."""
    jobs = _sample_jobs()
    metrics = {
        "active": 18,
        "due_today": 4,
        "awaiting_pickup": 3,
    }
    filters = {
        "query": "",
        "stage": "all",
        "show_archived": False,
    }
    return render_template(
        "jobs/index.html",
        jobs=jobs,
        metrics=metrics,
        filters=filters,
    )


@bp.get("/kanban")
def kanban():
    """Render the jobs kanban board."""
    jobs = _sample_jobs()
    columns = _group_jobs_by_department(jobs)
    filters = {
        "search": "",
        "color": "",
        "status": "",
    }
    color_options = sorted({job["color"] for job in jobs if job.get("color")})
    status_options = sorted({job["status"] for job in jobs if job.get("status")})
    return render_template(
        "jobs/kanban.html",
        columns_meta=_KANBAN_COLUMNS,
        columns=columns,
        filters=filters,
        color_options=color_options,
        status_options=status_options,
    )


def _find_job(job_id: int) -> dict[str, str | int | bool] | None:
    for job in _sample_jobs():
        if int(job["id"]) == job_id:
            return job
    return None


@bp.get("/<int:job_id>/")
def detail(job_id: int):
    """Render the job detail view."""
    job = _find_job(job_id)
    if not job:
        # TODO: replace with real 404 handling once repositories wired.
        return (
            render_template(
                "errors/error.html",
                error="Job Not Found",
                message="We couldn't locate that job. It may have been archived.",
            ),
            404,
        )

    photos = [
        {
            "url": "/static/img/job-photo-placeholder.svg",
            "label": "Before prep (placeholder)",
        },
        {
            "url": "/static/img/job-photo-placeholder.svg",
            "label": "After coating (placeholder)",
        },
    ]
    return render_template(
        "jobs/detail.html",
        job=job,
        photos=photos,
        is_admin=True,
    )


@bp.get("/<int:job_id>/edit")
def edit(job_id: int):
    """Render the job edit form (placeholder)."""
    job = _find_job(job_id)
    if not job:
        return (
            render_template(
                "errors/error.html",
                error="Job Not Found",
                message="We couldn't locate that job. It may have been archived.",
            ),
            404,
        )

    photos = [
        {
            "url": "/static/img/job-photo-placeholder.svg",
            "label": "Before prep (placeholder)",
        },
        {
            "url": "/static/img/job-photo-placeholder.svg",
            "label": "After coating (placeholder)",
        },
    ]
    return render_template(
        "jobs/edit.html",
        job=job,
        photos=photos,
        form_options=_FORM_OPTIONS,
        departments=_DEPARTMENTS,
        is_admin=True,
    )
