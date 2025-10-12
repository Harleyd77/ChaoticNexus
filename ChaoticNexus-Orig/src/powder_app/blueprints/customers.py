from __future__ import annotations

from datetime import datetime

from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from ..core.customers import normalize_company
from ..core.db import INTEGRITY_ERRORS, db_execute, db_query_all, db_query_one
from ..core.security import has_perm, is_admin, require_admin
from ..services import customers_service
from werkzeug.security import generate_password_hash

bp = Blueprint("customers", __name__)


@bp.route("/customers/search.json")
def customers_search():
    query = (request.args.get("q") or "").strip()
    exact = request.args.get("exact") == "1"
    if not query:
        return jsonify([])
    if exact:
        row = db_query_one("SELECT * FROM customers WHERE company=?", (query,))
        return jsonify([dict(row)]) if row else jsonify([])
    like = f"%{query}%"
    rows = db_query_all(
        """
        SELECT * FROM customers
        WHERE company LIKE ? OR contact_name LIKE ?
        ORDER BY LOWER(company) ASC LIMIT 10
        """,
        (like, like),
    )
    return jsonify([dict(r) for r in rows])


@bp.route("/customers")
def customers_page():
    if not (is_admin() or has_perm("see_customers")):
        return redirect(url_for("login", next=url_for("customers_page")))
    return render_template(
        "customers/index.html",
        is_admin=is_admin(),
    )


@bp.route("/api/customers")
def api_customers_list():
    """API endpoint for customer summary list"""
    if not (is_admin() or has_perm("see_customers")):
        return jsonify({"error": "Unauthorized"}), 403
    
    customers = customers_service.get_customers_summary()
    return jsonify(customers)


@bp.route("/api/customers/<int:customer_id>/dashboard")
def api_customer_dashboard(customer_id: int):
    """API endpoint for customer mini-dashboard"""
    if not (is_admin() or has_perm("see_customers")):
        return jsonify({"error": "Unauthorized"}), 403
    
    dashboard = customers_service.get_customer_dashboard(customer_id)
    if not dashboard:
        return jsonify({"error": "Customer not found"}), 404
    
    return jsonify(dashboard)


@bp.route("/customers/save", methods=["POST"])
def customers_save():
    if not is_admin():
        return redirect(url_for("login", next=url_for("customers_page")))
    form = request.form
    now = datetime.now().isoformat()
    cust_id = form.get("id")
    company = normalize_company(form.get("company") or "")
    if not company:
        abort(400, "Company is required")
    if cust_id:
        db_execute(
            """
            UPDATE customers
               SET company=?, contact_name=?, phone=?, email=?, address=?, notes=?,
                    street=?, city=?, region=?, postal_code=?, country=?, website=?, tax_id=?, account_number=?, terms=?, status=?, updated_at=?, phone_ext=?
             WHERE id=?
            """,
            (
                company,
                form.get("contact_name"),
                form.get("phone"),
                form.get("email"),
                form.get("address"),
                form.get("notes"),
                form.get("street"),
                form.get("city"),
                form.get("region"),
                form.get("postal_code"),
                form.get("country"),
                form.get("website"),
                form.get("tax_id"),
                form.get("account_number"),
                form.get("terms"),
                form.get("status"),
                now,
                form.get("phone_ext"),
                cust_id,
            ),
        )
    else:
        existing = db_query_one(
            "SELECT id FROM customers WHERE lower(trim(company)) = lower(trim(?))",
            (company,),
        )
        if existing:
            db_execute(
                """
                UPDATE customers
                   SET company=?, contact_name=?, phone=?, email=?, address=?, notes=?,
                       street=?, city=?, region=?, postal_code=?, country=?, website=?, tax_id=?, account_number=?, terms=?, status=?, updated_at=?, phone_ext=?
                 WHERE id=?
                """,
                (
                    company,
                    form.get("contact_name"),
                    form.get("phone"),
                    form.get("email"),
                    form.get("address"),
                    form.get("notes"),
                    form.get("street"),
                    form.get("city"),
                    form.get("region"),
                    form.get("postal_code"),
                    form.get("country"),
                    form.get("website"),
                    form.get("tax_id"),
                    form.get("account_number"),
                    form.get("terms"),
                    form.get("status"),
                    now,
                    form.get("phone_ext"),
                    existing["id"],
                ),
            )
        else:
            try:
                db_execute(
                    """
                    INSERT INTO customers (
                        company, contact_name, phone, email, address, notes, created_at,
                        street, city, region, postal_code, country, website, tax_id, account_number, terms, status, updated_at, phone_ext
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        company,
                        form.get("contact_name"),
                        form.get("phone"),
                        form.get("email"),
                        form.get("address"),
                        form.get("notes"),
                        now,
                        form.get("street"),
                        form.get("city"),
                        form.get("region"),
                        form.get("postal_code"),
                        form.get("country"),
                        form.get("website"),
                        form.get("tax_id"),
                        form.get("account_number"),
                        form.get("terms"),
                        form.get("status"),
                        now,
                        form.get("phone_ext"),
                    ),
                )
            except INTEGRITY_ERRORS:
                row = db_query_one(
                    "SELECT id FROM customers WHERE lower(trim(company)) = lower(trim(?))",
                    (company,),
                )
                if row:
                    db_execute(
                        """
                        UPDATE customers
                           SET company=?, contact_name=?, phone=?, email=?, address=?, notes=?,
                               street=?, city=?, region=?, postal_code=?, country=?, website=?, tax_id=?, account_number=?, terms=?, status=?, updated_at=?, phone_ext=?
                         WHERE id=?
                        """,
                        (
                            company,
                            form.get("contact_name"),
                            form.get("phone"),
                            form.get("email"),
                            form.get("address"),
                            form.get("notes"),
                            form.get("street"),
                            form.get("city"),
                            form.get("region"),
                            form.get("postal_code"),
                            form.get("country"),
                            form.get("website"),
                            form.get("tax_id"),
                            form.get("account_number"),
                            form.get("terms"),
                            form.get("status"),
                            now,
                            form.get("phone_ext"),
                            row["id"],
                        ),
                    )
    return redirect(url_for("customers_page"))


@bp.route("/customers/<int:cust_id>/delete", methods=["POST"])
def customers_delete(cust_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("customers_page")))
    db_execute("DELETE FROM contacts WHERE customer_id=?", (cust_id,))
    db_execute("DELETE FROM customers WHERE id=?", (cust_id,))
    return redirect(url_for("customers_page"))


@bp.route("/customers/<int:cust_id>/contacts.json")
def contacts_json(cust_id: int):
    rows = db_query_all(
        "SELECT id, name, phone, ext, email, role, notes FROM contacts WHERE customer_id=? ORDER BY id DESC",
        (cust_id,),
    )
    return jsonify([dict(r) for r in rows])


@bp.route("/customers/<int:cust_id>/contacts/add", methods=["POST"])
def contacts_add(cust_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("customers_page")))
    form = request.form
    now = datetime.now().isoformat()
    db_execute(
        """
        INSERT INTO contacts (customer_id, name, phone, ext, email, role, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cust_id,
            form.get("name"),
            form.get("phone"),
            form.get("ext"),
            form.get("email"),
            form.get("role"),
            form.get("notes"),
            now,
        ),
    )
    return redirect(url_for("customer_detail", cust_id=cust_id))


@bp.route("/customers/<int:cust_id>/contacts/<int:ct_id>/save", methods=["POST"])
def contacts_save(cust_id: int, ct_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("customers_page")))
    form = request.form
    db_execute(
        """
        UPDATE contacts SET name=?, phone=?, ext=?, email=?, role=?, notes=?, updated_at=?
         WHERE id=? AND customer_id=?
        """,
        (
            form.get("name"),
            form.get("phone"),
            form.get("ext"),
            form.get("email"),
            form.get("role"),
            form.get("notes"),
            datetime.now().isoformat(),
            ct_id,
            cust_id,
        ),
    )
    return redirect(url_for("customer_detail", cust_id=cust_id))


@bp.route("/customers/<int:cust_id>/contacts/<int:ct_id>/delete", methods=["POST"])
def contacts_delete(cust_id: int, ct_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("customers_page")))
    db_execute("DELETE FROM contacts WHERE id=? AND customer_id=?", (ct_id, cust_id))
    return redirect(url_for("customer_detail", cust_id=cust_id))


@bp.route("/customers/<int:cust_id>")
def customer_detail(cust_id: int):
    """Customer profile page (view/locked by default)"""
    cust = db_query_one("SELECT * FROM customers WHERE id=?", (cust_id,))
    if not cust:
        abort(404)
    jobs = db_query_all(
        """
        SELECT id, created_at, type, description, status, color, due_by, date_in
          FROM jobs
         WHERE company = ?
         AND (archived IS NULL OR archived = 0)
         ORDER BY id DESC
        """,
        (cust["company"],),
    )
    contacts = db_query_all("SELECT * FROM contacts WHERE customer_id=? ORDER BY id DESC", (cust_id,))
    return render_template(
        "customers/profile.html",
        c=cust,
        jobs=jobs,
        contacts=contacts,
        is_admin=is_admin(),
    )


@bp.route("/api/customers/<int:customer_id>", methods=["PATCH"])
def api_customer_update(customer_id: int):
    """API endpoint for updating customer (from profile edit mode)"""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json() or {}
    updated = customers_service.update_customer(customer_id, data)
    return jsonify(dict(updated))


@bp.route("/customers/<int:cust_id>/save", methods=["POST"])
def customer_detail_save(cust_id: int):
    if not is_admin():
        return redirect(url_for("login", next=url_for("customer_detail", cust_id=cust_id)))
    form = request.form
    now = datetime.now().isoformat()
    company = normalize_company(form.get("company") or "")
    if not company:
        abort(400, "Company is required")
    db_execute(
        """
        UPDATE customers SET
            company=?, contact_name=?, phone=?, email=?, address=?, notes=?,
            street=?, city=?, region=?, postal_code=?, country=?, website=?, tax_id=?, account_number=?, terms=?, status=?, updated_at=?
         WHERE id=?
        """,
        (
            company, form.get("contact_name"), form.get("phone"), form.get("email"), form.get("address"), form.get("notes"),
            form.get("street"), form.get("city"), form.get("region"), form.get("postal_code"), form.get("country"),
            form.get("website"), form.get("tax_id"), form.get("account_number"), form.get("terms"), form.get("status"),
            now, cust_id,
        ),
    )
    return redirect(url_for("customer_detail", cust_id=cust_id))


# ============================================================================
# ADMIN CUSTOMER PORTAL ACCOUNT MANAGEMENT
# ============================================================================

@bp.route("/admin/customer-accounts")
def admin_customer_accounts():
    """Admin page to manage customer portal accounts"""
    if not is_admin():
        return redirect(url_for("login", next=url_for("admin_customer_accounts")))
    
    # Get all customer accounts with their associated customer records
    accounts = db_query_all("""
        SELECT 
            ca.*,
            c.company,
            c.contact_name,
            c.phone as customer_phone,
            c.email as customer_email
        FROM customer_accounts ca
        LEFT JOIN customers c ON LOWER(TRIM(ca.company_name)) = LOWER(TRIM(c.company))
        ORDER BY ca.created_at DESC
    """)
    
    return render_template(
        "customers/admin_accounts.html",
        accounts=accounts,
        is_admin=is_admin(),
    )


@bp.route("/api/admin/customer-accounts")
def api_admin_customer_accounts():
    """API endpoint for customer accounts list (admin only)"""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    
    accounts = db_query_all("""
        SELECT 
            ca.id,
            ca.email,
            ca.first_name,
            ca.last_name,
            ca.company_name,
            ca.phone,
            ca.is_active,
            ca.email_verified,
            ca.created_at,
            ca.last_login,
            c.company,
            c.contact_name
        FROM customer_accounts ca
        LEFT JOIN customers c ON LOWER(TRIM(ca.company_name)) = LOWER(TRIM(c.company))
        ORDER BY ca.created_at DESC
    """)
    
    return jsonify([dict(account) for account in accounts])


@bp.route("/admin/customer-accounts/<int:account_id>")
def admin_customer_account_detail(account_id):
    """Admin page to view/edit specific customer account"""
    if not is_admin():
        return redirect(url_for("login", next=url_for("admin_customer_account_detail", account_id=account_id)))
    
    account = db_query_one("""
        SELECT 
            ca.*,
            c.id as customer_id,
            c.company,
            c.contact_name,
            c.phone as customer_phone,
            c.email as customer_email,
            c.address,
            c.notes
        FROM customer_accounts ca
        LEFT JOIN customers c ON LOWER(TRIM(ca.company_name)) = LOWER(TRIM(c.company))
        WHERE ca.id = ?
    """, (account_id,))
    
    if not account:
        abort(404)
    
    # Get customer's jobs
    jobs = []
    if account.get('customer_id'):
        jobs = db_query_all("""
            SELECT id, created_at, type, description, status, color, due_by, date_in
            FROM jobs
            WHERE company = ?
            AND (archived IS NULL OR archived = 0)
            ORDER BY id DESC
            LIMIT 10
        """, (account['company'],))
    
    return render_template(
        "customers/admin_account_detail.html",
        account=account,
        jobs=jobs,
        is_admin=is_admin(),
    )


@bp.route("/api/admin/customer-accounts/<int:account_id>", methods=["PATCH"])
def api_admin_update_customer_account(account_id):
    """API endpoint to update customer account (admin only)"""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    if 'first_name' in data and not data['first_name'].strip():
        return jsonify({"error": "First name is required"}), 400
    if 'last_name' in data and not data['last_name'].strip():
        return jsonify({"error": "Last name is required"}), 400
    if 'email' in data and not data['email'].strip():
        return jsonify({"error": "Email is required"}), 400
    
    # Check for email conflicts
    if 'email' in data:
        existing = db_query_one(
            "SELECT id FROM customer_accounts WHERE email = ? AND id != ?",
            (data['email'].strip().lower(), account_id)
        )
        if existing:
            return jsonify({"error": "Email already exists"}), 400
    
    # Build update query dynamically
    updates = []
    params = []
    
    for field in ['first_name', 'last_name', 'email', 'company_name', 'phone', 'address']:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field].strip() if data[field] else None)
    
    if 'is_active' in data:
        updates.append("is_active = ?")
        params.append(1 if data['is_active'] else 0)
    
    if 'email_verified' in data:
        updates.append("email_verified = ?")
        params.append(1 if data['email_verified'] else 0)
    
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(account_id)
        
        db_execute(
            f"UPDATE customer_accounts SET {', '.join(updates)} WHERE id = ?",
            params
        )
    
    # Get updated account
    updated_account = db_query_one("SELECT * FROM customer_accounts WHERE id = ?", (account_id,))
    return jsonify(dict(updated_account))


@bp.route("/api/admin/customer-accounts/<int:account_id>/password", methods=["POST"])
def api_admin_reset_customer_password(account_id):
    """API endpoint to reset customer password (admin only)"""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json() or {}
    new_password = data.get('password', '').strip()
    
    if not new_password:
        return jsonify({"error": "Password is required"}), 400
    
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    if not any(c.isupper() for c in new_password):
        return jsonify({"error": "Password must contain at least one uppercase letter"}), 400
    
    if not any(c.isdigit() for c in new_password):
        return jsonify({"error": "Password must contain at least one number"}), 400
    
    # Hash the new password
    password_hash = generate_password_hash(new_password)
    
    # Update the password
    db_execute(
        "UPDATE customer_accounts SET password_hash = ?, updated_at = ? WHERE id = ?",
        (password_hash, datetime.now().isoformat(), account_id)
    )
    
    return jsonify({"success": True, "message": "Password updated successfully"})


@bp.route("/api/admin/customer-accounts/<int:account_id>/toggle-active", methods=["POST"])
def api_admin_toggle_customer_account(account_id):
    """API endpoint to toggle customer account active status (admin only)"""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json() or {}
    is_active = data.get('is_active', True)
    
    db_execute(
        "UPDATE customer_accounts SET is_active = ?, updated_at = ? WHERE id = ?",
        (1 if is_active else 0, datetime.now().isoformat(), account_id)
    )
    
    status = "activated" if is_active else "deactivated"
    return jsonify({"success": True, "message": f"Account {status} successfully"})


@bp.route("/api/admin/customer-accounts/<int:account_id>", methods=["DELETE"])
def api_admin_delete_customer_account(account_id):
    """API endpoint to delete customer account (admin only)"""
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    
    # Check if account exists
    account = db_query_one("SELECT id FROM customer_accounts WHERE id = ?", (account_id,))
    if not account:
        return jsonify({"error": "Account not found"}), 404
    
    # Delete the account
    db_execute("DELETE FROM customer_accounts WHERE id = ?", (account_id,))
    
    return jsonify({"success": True, "message": "Account deleted successfully"})