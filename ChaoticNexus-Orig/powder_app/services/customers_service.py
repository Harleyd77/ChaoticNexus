"""
Customer service layer for data access and KPI aggregation.
Provides summary and detailed analytics for customer management.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ..core.db import db_query_all, db_query_one


def get_customers_summary() -> list[dict[str, Any]]:
    """
    Get customer summary list with job stats.
    Used for the main customers list page (collapsed cards).
    """
    customers = db_query_all(
        """
        SELECT 
            id, company, contact_name, phone, email, address,
            street, city, region, postal_code
        FROM customers
        ORDER BY LOWER(company) ASC
    """
    )

    result = []
    for c in customers:
        # Get job stats for this customer
        stats = db_query_one(
            """
            SELECT 
                COUNT(CASE WHEN status IN ('in_work', 'waiting_material') THEN 1 END) as active_jobs,
                COUNT(CASE WHEN status = 'queued' THEN 1 END) as queued_jobs,
                COUNT(CASE WHEN status IN ('ready_pickup', 'completed') 
                      AND completed_at > ? THEN 1 END) as completed_recent
            FROM jobs
            WHERE company = ? AND (archived IS NULL OR archived = 0)
        """,
            ((datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"), c["company"]),
        )

        # Build address_short
        address_parts = []
        if c.get("street"):
            address_parts.append(c["street"])
        if c.get("city"):
            address_parts.append(c["city"])
        if c.get("region"):
            address_parts.append(c["region"])
        address_short = ", ".join(address_parts) if address_parts else c.get("address", "")

        result.append(
            {
                "id": c["id"],
                "company": c["company"] or "",
                "contact_name": c["contact_name"] or "",
                "phone": c["phone"] or "",
                "email": c["email"] or "",
                "stats": {
                    "active_jobs": int(stats["active_jobs"] or 0),
                    "queued_jobs": int(stats["queued_jobs"] or 0),
                    "completed_recent": int(stats["completed_recent"] or 0),
                },
                "address_short": address_short,
            }
        )

    return result


def get_customer_dashboard(customer_id: int) -> dict[str, Any]:
    """
    Get mini-dashboard payload for a single customer.
    Includes KPIs, work mix, and recent activity.
    """
    customer = db_query_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
    if not customer:
        return {}

    company = customer["company"]

    # === KPIs ===
    # Active jobs (in_work, waiting_material)
    active = db_query_one(
        """
        SELECT COUNT(*) as count 
        FROM jobs 
        WHERE company = ? 
        AND status IN ('in_work', 'waiting_material')
        AND (archived IS NULL OR archived = 0)
    """,
        (company,),
    )
    active_jobs = int(active["count"] or 0)

    # Average turnaround for last 10 completed jobs
    completed_jobs = db_query_all(
        """
        SELECT date_in, completed_at
        FROM jobs
        WHERE company = ?
        AND status IN ('completed', 'ready_pickup')
        AND date_in IS NOT NULL
        AND completed_at IS NOT NULL
        AND (archived IS NULL OR archived = 0)
        ORDER BY completed_at DESC
        LIMIT 10
    """,
        (company,),
    )

    avg_turnaround = None
    if completed_jobs:
        turnarounds = []
        for job in completed_jobs:
            try:
                # Parse dates (format: YYYY-MM-DD or ISO timestamp)
                date_in_str = job["date_in"][:10] if job["date_in"] else None
                completed_str = job["completed_at"][:10] if job["completed_at"] else None
                if date_in_str and completed_str:
                    date_in = datetime.strptime(date_in_str, "%Y-%m-%d")
                    completed = datetime.strptime(completed_str, "%Y-%m-%d")
                    days = (completed - date_in).days
                    if days >= 0:
                        turnarounds.append(days)
            except (ValueError, TypeError):
                continue
        if turnarounds:
            avg_turnaround = round(sum(turnarounds) / len(turnarounds), 1)

    # On-time percentage (last 90 days)
    ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    on_time_data = db_query_one(
        """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE 
                WHEN completed_at IS NOT NULL 
                AND due_by IS NOT NULL 
                AND completed_at <= due_by 
                THEN 1 END) as on_time
        FROM jobs
        WHERE company = ?
        AND status IN ('completed', 'ready_pickup')
        AND completed_at >= ?
        AND due_by IS NOT NULL
        AND (archived IS NULL OR archived = 0)
    """,
        (company, ninety_days_ago),
    )

    on_time_pct = None
    if on_time_data and on_time_data["total"] and int(on_time_data["total"]) > 0:
        on_time_pct = round((int(on_time_data["on_time"] or 0) / int(on_time_data["total"])) * 100)

    # Jobs this month
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    jobs_this_month = db_query_one(
        """
        SELECT COUNT(*) as count
        FROM jobs
        WHERE company = ?
        AND created_at >= ?
        AND (archived IS NULL OR archived = 0)
    """,
        (company, month_start),
    )
    jobs_this_month_count = int(jobs_this_month["count"] or 0)

    # Redo count (last 12 months)
    twelve_months_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    redo_pattern = "%redo%"
    redo_count = db_query_one(
        """
        SELECT COUNT(*) as count
        FROM jobs
        WHERE company = ?
        AND created_at >= ?
        AND (LOWER(notes) LIKE ? OR LOWER(description) LIKE ?)
        AND (archived IS NULL OR archived = 0)
    """,
        (company, twelve_months_ago, redo_pattern, redo_pattern),
    )
    redo_count_val = int(redo_count["count"] or 0)

    kpis = {
        "active_jobs": active_jobs,
        "avg_turnaround_days_10": avg_turnaround,
        "on_time_pct_90d": on_time_pct,
        "jobs_this_month": jobs_this_month_count,
        "lifetime_revenue": None,  # Not implemented yet
        "redo_count_12m": redo_count_val,
    }

    # === Work Mix ===
    # Job types (last 6 months)
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    job_types = db_query_all(
        """
        SELECT type, COUNT(*) as count
        FROM jobs
        WHERE company = ?
        AND created_at >= ?
        AND type IS NOT NULL
        AND type != ''
        AND (archived IS NULL OR archived = 0)
        GROUP BY type
        ORDER BY count DESC
    """,
        (company, six_months_ago),
    )

    # Top 3 powder colors
    top_powders = db_query_all(
        """
        SELECT 
            color,
            COUNT(*) as count
        FROM jobs
        WHERE company = ?
        AND color IS NOT NULL
        AND color != ''
        AND color != 'Not specified'
        AND (archived IS NULL OR archived = 0)
        GROUP BY color
        ORDER BY count DESC
        LIMIT 3
    """,
        (company,),
    )

    # Try to parse powder info (format varies)
    powder_list = []
    for p in top_powders:
        color_str = p["color"] or ""
        # Simple parsing - actual format may vary
        powder_list.append(
            {
                "brand": None,  # Would need parsing from color field
                "product_code": None,  # Would need parsing
                "ral": color_str,
                "count": int(p["count"] or 0),
            }
        )

    mix = {
        "job_types": [{"type": jt["type"], "count": int(jt["count"] or 0)} for jt in job_types],
        "top_powders": powder_list,
    }

    # === Activity ===
    # Recent jobs (5 most recent)
    recent_jobs = db_query_all(
        """
        SELECT id, type, status, due_by, color
        FROM jobs
        WHERE company = ?
        AND (archived IS NULL OR archived = 0)
        ORDER BY id DESC
        LIMIT 5
    """,
        (company,),
    )

    recent_jobs_list = []
    for job in recent_jobs:
        recent_jobs_list.append(
            {
                "id": job["id"],
                "type": job["type"] or "N/A",
                "status": job["status"] or "unknown",
                "due_date": job["due_by"] or None,
                "color": job["color"] or "Not specified",
            }
        )

    # Last interaction (most recent job or update)
    last_job = db_query_one(
        """
        SELECT created_at, updated_at
        FROM customers
        WHERE id = ?
    """,
        (customer_id,),
    )

    last_interaction = None
    if last_job:
        last_at = last_job.get("updated_at") or last_job.get("created_at")
        if last_at:
            last_interaction = {
                "at": last_at,
                "by": None,  # Would need user tracking
                "note": None,
            }

    activity = {
        "recent_jobs": recent_jobs_list,
        "last_interaction": last_interaction,
        "open_quotes": None,  # Not implemented
        "outstanding_balance": None,  # Not implemented
    }

    return {
        "kpis": kpis,
        "mix": mix,
        "activity": activity,
    }


def update_customer(customer_id: int, data: dict[str, Any]) -> dict[str, Any]:
    """
    Update customer with partial data.
    Returns the full updated customer record.
    """
    from ..core.customers import normalize_company
    from ..core.db import db_execute

    allowed_fields = [
        "company",
        "contact_name",
        "phone",
        "email",
        "address",
        "notes",
        "street",
        "city",
        "region",
        "postal_code",
        "country",
        "website",
        "tax_id",
        "account_number",
        "terms",
        "status",
        "phone_ext",
    ]

    updates = []
    params = []

    for field in allowed_fields:
        if field in data:
            value = data[field]
            if field == "company" and value:
                value = normalize_company(value)
            updates.append(f"{field} = ?")
            params.append(value)

    if not updates:
        # No fields to update, just return current record
        return db_query_one("SELECT * FROM customers WHERE id = ?", (customer_id,))

    # Add updated_at
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())

    # Add customer_id for WHERE clause
    params.append(customer_id)

    sql = f"UPDATE customers SET {', '.join(updates)} WHERE id = ?"
    db_execute(sql, tuple(params))

    return db_query_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
