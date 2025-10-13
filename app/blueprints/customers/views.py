"""HTTP endpoints for the Customers blueprint."""

from __future__ import annotations

from flask import flash, jsonify, redirect, render_template, request, url_for

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


@bp.route("/<int:cust_id>", methods=["GET", "POST"])
def profile(cust_id: int):
    """Customer profile view/edit page."""
    customer = customer_repo.get_customer(cust_id)
    if not customer:
        flash("Customer not found", "error")
        return redirect(url_for("customers.index"))

    if request.method == "POST":
        updated = customer_repo.update_customer(
            cust_id,
            company=request.form.get("company") or customer.company,
            contact_name=request.form.get("contact_name") or customer.contact_name,
            email=request.form.get("email") or customer.email,
            phone=request.form.get("phone") or customer.phone,
            street=request.form.get("street") or customer.street,
            city=request.form.get("city") or customer.city,
            region=request.form.get("region") or customer.region,
            postal_code=request.form.get("postal_code") or customer.postal_code,
            account_number=request.form.get("account_number") or customer.account_number,
            terms=request.form.get("terms") or customer.terms,
            status=request.form.get("status") or customer.status,
            notes=request.form.get("notes") or customer.notes,
        )
        flash("Customer updated" if updated else "Update failed", "success" if updated else "error")
        return redirect(url_for("customers.profile", cust_id=cust_id))

    return render_template("customers/profile.html", customer=customer, is_admin=True)


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


@bp.get("/contacts.json")
def contacts_json():
    """Return contacts for a given customer by query param id (legacy search compat)."""
    customer_id = request.args.get("id")
    if not customer_id:
        return jsonify([])
    contacts = customer_repo.list_contacts(int(customer_id))
    return jsonify(
        [{"id": c.id, "name": c.name, "phone": c.phone, "email": c.email} for c in contacts]
    )


@bp.get("/search.json")
def search_json():
    q = request.args.get("q", "").strip()
    rows = customer_repo.search_customers(q) if q else []
    return jsonify(
        [
            {
                "id": c.id,
                "company": c.company,
                "contact_name": c.contact_name,
                "phone": c.phone,
                "email": c.email,
            }
            for c in rows
        ]
    )


@bp.get("/<int:cust_id>/contacts.json")
def contacts_for_customer(cust_id: int):
    contacts = customer_repo.list_contacts(cust_id)
    return jsonify(
        [{"id": c.id, "name": c.name, "phone": c.phone, "email": c.email} for c in contacts]
    )


@bp.post("/<int:cust_id>/contacts/add")
def add_contact(cust_id: int):
    name = request.form.get("name", "")
    phone = request.form.get("phone")
    email = request.form.get("email")
    if not name.strip():
        flash("Contact name is required", "error")
        return redirect(url_for("customers.index"))
    customer_repo.add_contact(cust_id, name=name, phone=phone, email=email)
    flash("Contact added", "success")
    return redirect(url_for("customers.index"))


@bp.post("/<int:cust_id>/contacts/<int:ct_id>/save")
def save_contact(cust_id: int, ct_id: int):
    updated = customer_repo.update_contact(
        cust_id,
        ct_id,
        name=request.form.get("name"),
        phone=request.form.get("phone"),
        email=request.form.get("email"),
    )
    flash("Contact saved" if updated else "Contact not found", "success" if updated else "error")
    return redirect(url_for("customers.index"))


@bp.post("/<int:cust_id>/contacts/<int:ct_id>/delete")
def delete_contact(cust_id: int, ct_id: int):
    ok = customer_repo.delete_contact(cust_id, ct_id)
    flash("Contact deleted" if ok else "Contact not found", "success" if ok else "error")
    return redirect(url_for("customers.index"))
