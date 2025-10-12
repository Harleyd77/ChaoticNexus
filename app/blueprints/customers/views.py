"""HTTP endpoints for the Customers blueprint."""

from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from app.repositories import customer_repo

from . import bp


@bp.route("/")
def index():
    """Customers list page."""
    customers = customer_repo.list_customers()
    return render_template(
        "customers/index.html",
        is_admin=True,
        customers=customers,
    )


@bp.route("/new", methods=["GET", "POST"])
def new_customer():
    """Create a new customer record."""
    if request.method == "POST":
        form = request.form
        company = form.get("company", "").strip()
        if not company:
            flash("Company name is required", "error")
        else:
            customer_repo.create_customer(
                company=company,
                contact_name=form.get("contact_name", "").strip() or None,
                email=form.get("email", "").strip() or None,
                phone=form.get("phone", "").strip() or None,
                street=form.get("street", "").strip() or None,
                city=form.get("city", "").strip() or None,
                region=form.get("region", "").strip() or None,
                postal_code=form.get("postal_code", "").strip() or None,
                account_number=form.get("account_number", "").strip() or None,
                terms=form.get("terms", "").strip() or None,
                status=form.get("status", "").strip() or "Active",
                notes=form.get("notes", "").strip() or None,
            )
            flash("Customer added successfully", "success")
            return redirect(url_for("customers.index"))

    return render_template("customers/new.html", is_admin=True)
