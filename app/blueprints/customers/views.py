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
        company = request.form.get("company", "").strip()
        contact_name = request.form.get("contact_name", "").strip() or None
        email = request.form.get("email", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        street = request.form.get("street", "").strip() or None
        city = request.form.get("city", "").strip() or None
        region = request.form.get("region", "").strip() or None
        postal_code = request.form.get("postal_code", "").strip() or None
        account_number = request.form.get("account_number", "").strip() or None
        terms = request.form.get("terms", "").strip() or None
        status = request.form.get("status", "").strip() or "Active"
        notes = request.form.get("notes", "").strip() or None

        errors = []
        if not company:
            errors.append("Company name is required.")
        if email and "@" not in email:
            errors.append("Enter a valid email address.")

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            customer_repo.create_customer(
                company=company,
                contact_name=contact_name,
                email=email,
                phone=phone,
                street=street,
                city=city,
                region=region,
                postal_code=postal_code,
                account_number=account_number,
                terms=terms,
                status=status,
                notes=notes,
            )
            flash("Customer added successfully", "success")
            return redirect(url_for("customers.index"))

        form_data = {
            "company": company,
            "contact_name": contact_name or "",
            "email": email or "",
            "phone": phone or "",
            "street": street or "",
            "city": city or "",
            "region": region or "",
            "postal_code": postal_code or "",
            "account_number": account_number or "",
            "terms": terms or "",
            "status": status,
            "notes": notes or "",
        }
        return render_template("customers/new.html", is_admin=True, form_data=form_data)

    return render_template("customers/new.html", is_admin=True, form_data={})
