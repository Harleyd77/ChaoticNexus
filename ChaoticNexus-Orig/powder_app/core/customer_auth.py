"""
Customer Authentication Utilities

Provides functions to detect and work with customer authentication across the app.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from flask import session
from werkzeug.security import check_password_hash

from .db import get_db

_CUSTOMER_SESSION_KEYS = ("customer_id", "customer_session_token", "customer_name")


def _clear_customer_session_keys() -> None:
    for key in _CUSTOMER_SESSION_KEYS:
        session.pop(key, None)


def get_current_customer():
    """Get the currently logged-in customer across the entire app."""
    customer_id = session.get("customer_id")
    session_token = session.get("customer_session_token")

    if not customer_id or not session_token:
        return None

    db = get_db()
    customer = db.execute(
        """
        SELECT ca.*, cs.expires_at
        FROM customer_accounts ca
        JOIN customer_sessions cs ON ca.id = cs.customer_id
        WHERE ca.id = ?
          AND cs.session_token = ?
          AND cs.is_active = TRUE
          AND cs.expires_at > NOW()
    """,
        (customer_id, session_token),
    ).fetchone()

    return customer


def is_customer_logged_in():
    """Check if a customer is currently logged in."""
    return get_current_customer() is not None


def get_customer_contact_info():
    """Get formatted contact information for the current customer."""
    customer = get_current_customer()
    if not customer:
        return {}

    return {
        "first_name": customer["first_name"],
        "last_name": customer["last_name"],
        "company_name": customer["company_name"],
        "phone": customer["phone"],
        "email": customer["email"],
        "address": customer["address"],
        "full_name": f"{customer['first_name']} {customer['last_name']}".strip(),
        "contact_name": f"{customer['first_name']} {customer['last_name']}".strip(),
        "company": customer["company_name"]
        or f"{customer['first_name']} {customer['last_name']}".strip(),
    }


def can_customer_access_intake():
    """Check if customer can access intake forms."""
    return is_customer_logged_in()


def populate_intake_form_with_customer_data(form_data):
    """Populate intake form data with current customer information."""
    customer_info = get_customer_contact_info()
    if not customer_info:
        return form_data

    field_mapping = {
        "first_name": "first_name",
        "last_name": "last_name",
        "contact_name": "contact_name",
        "company_name": "company",
        "company": "company",
        "phone": "phone",
        "email": "email",
    }

    populated_data = form_data.copy()
    for customer_field, form_field in field_mapping.items():
        if customer_field in customer_info and not populated_data.get(form_field):
            populated_data[form_field] = customer_info[customer_field]

    return populated_data


def create_customer_context():
    """Create template context for customer information."""
    customer = get_current_customer()
    if not customer:
        return {"customer_logged_in": False}

    return {
        "customer_logged_in": True,
        "customer": customer,
        "customer_info": get_customer_contact_info(),
        "can_access_customer_portal": True,
    }


def authenticate_customer_credentials(
    email: str, password: str
) -> Tuple[Optional[dict], Optional[str]]:
    """Validate customer credentials.

    Returns a tuple of (customer_row, error_message). If authentication succeeds,
    the error_message will be None.
    """
    if not email or not password:
        return None, "Email and password are required"

    db = get_db()
    customer = db.execute(
        """
        SELECT id, email, password_hash, first_name, last_name, is_active
        FROM customer_accounts
        WHERE lower(email) = lower(?)
        """,
        (email,),
    ).fetchone()

    if not customer or not check_password_hash(customer["password_hash"], password):
        return None, "Invalid email or password"

    if not customer["is_active"]:
        return None, "Account is disabled. Please contact support."

    return customer, None


def start_customer_session(customer: dict) -> str:
    """Create a persistent customer session and update session storage."""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=30)

    db = get_db()
    db.execute(
        """
        INSERT INTO customer_sessions (customer_id, session_token, expires_at)
        VALUES (?, ?, ?)
        """,
        (customer["id"], session_token, expires_at),
    )
    db.execute(
        """
        UPDATE customer_accounts
        SET last_login = ?
        WHERE id = ?
        """,
        (datetime.now(), customer["id"]),
    )
    db.commit()

    _clear_customer_session_keys()
    session["customer_id"] = customer["id"]
    session["customer_session_token"] = session_token
    session["customer_name"] = f"{customer['first_name']} {customer['last_name']}".strip()

    return session_token


def end_customer_session() -> None:
    """Invalidate any active customer session."""
    customer_id = session.get("customer_id")
    session_token = session.get("customer_session_token")

    if customer_id and session_token:
        db = get_db()
        db.execute(
            """
            UPDATE customer_sessions
            SET is_active = FALSE
            WHERE customer_id = ? AND session_token = ?
            """,
            (customer_id, session_token),
        )
        db.commit()

    _clear_customer_session_keys()
