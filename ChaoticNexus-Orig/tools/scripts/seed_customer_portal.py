"""Seed sample customer portal data for local testing.

Usage (from project root):
    docker exec powderapp-unified python -m tools.scripts.seed_customer_portal

This script clears customer portal related tables and inserts a few
customer accounts along with representative jobs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash


@dataclass
class SampleJob:
    created_at: datetime
    date_in: str
    due_by: str
    po: str
    job_type: str
    priority: str
    blast: str
    prep: str
    color: str
    color_source: str
    description: str
    notes: str
    status: str
    department: str
    customer_notes: str
    shop_notes: str
    submitted_by_customer: bool
    requires_approval: bool


@dataclass
class SampleCustomer:
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: str
    phone: str
    address: str
    created_at: datetime
    jobs: list[SampleJob] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


CUSTOMERS: list[SampleCustomer] = [
    SampleCustomer(
        email="alice@example.com",
        password="Password1",
        first_name="Alice",
        last_name="Anderson",
        company_name="Anderson Fabrication",
        phone="555-1000",
        address="123 Main St, Springfield",
        created_at=datetime(2025, 9, 1, 9, 0, 0),
        jobs=[
            SampleJob(
                created_at=datetime(2025, 9, 12, 8, 30, 0),
                date_in="2025-09-12",
                due_by="2025-09-20",
                po="AF-1001",
                job_type="Railing",
                priority="High",
                blast="Yes",
                prep="Sandblast",
                color="RAL 9005",
                color_source="Prismatic",
                description="Exterior railing set",
                notes="Rush order for install",
                status="In Progress",
                department="Prep",
                customer_notes="Need delivery before 9/22",
                shop_notes="Assign to Team A",
                submitted_by_customer=True,
                requires_approval=False,
            ),
            SampleJob(
                created_at=datetime(2025, 9, 18, 10, 15, 0),
                date_in="2025-09-18",
                due_by="2025-09-28",
                po="AF-1002",
                job_type="Industrial",
                priority="Normal",
                blast="No",
                prep="Degrease",
                color="RAL 3020",
                color_source="Tiger",
                description="Batch of machine guards",
                notes="",
                status="Queued",
                department="Intake",
                customer_notes="",
                shop_notes="",
                submitted_by_customer=True,
                requires_approval=True,
            ),
        ],
    ),
    SampleCustomer(
        email="bob@example.com",
        password="Password1",
        first_name="Bob",
        last_name="Bennett",
        company_name="Bennett Metalworks",
        phone="555-2000",
        address="456 Oak Ave, Riverton",
        created_at=datetime(2025, 9, 5, 10, 30, 0),
        jobs=[
            SampleJob(
                created_at=datetime(2025, 9, 19, 9, 0, 0),
                date_in="2025-09-19",
                due_by="2025-10-02",
                po="BM-2201",
                job_type="Automotive",
                priority="Normal",
                blast="Yes",
                prep="Sandblast",
                color="RAL 5015",
                color_source="Sherwin Williams",
                description="Truck frame components",
                notes="",
                status="Not Started",
                department="Intake",
                customer_notes="Please confirm color match",
                shop_notes="",
                submitted_by_customer=False,
                requires_approval=False,
            ),
            SampleJob(
                created_at=datetime(2025, 9, 22, 13, 45, 0),
                date_in="2025-09-22",
                due_by="2025-10-05",
                po="BM-2202",
                job_type="Custom",
                priority="High",
                blast="No",
                prep="Hand prep",
                color="RAL 9010",
                color_source="Axalta",
                description="Architectural panels",
                notes="",
                status="Ready for Pickup",
                department="Finishing",
                customer_notes="",
                shop_notes="QC completed 9/27",
                submitted_by_customer=True,
                requires_approval=False,
            ),
        ],
    ),
    SampleCustomer(
        email="carla@example.com",
        password="Password1",
        first_name="Carla",
        last_name="Cooper",
        company_name="Cooper Coatings",
        phone="555-3000",
        address="789 Pine Rd, Lakeside",
        created_at=datetime(2025, 9, 10, 14, 15, 0),
        jobs=[
            SampleJob(
                created_at=datetime(2025, 9, 21, 11, 0, 0),
                date_in="2025-09-21",
                due_by="2025-09-30",
                po="CC-3301",
                job_type="Batch",
                priority="Low",
                blast="No",
                prep="Wash",
                color="RAL 7035",
                color_source="Prismatic",
                description="Cabinet hardware batch",
                notes="",
                status="Completed",
                department="Shipping",
                customer_notes="Deliver with invoice",
                shop_notes="Shipped 9/29",
                submitted_by_customer=False,
                requires_approval=False,
            ),
        ],
    ),
]


def _connect() -> psycopg.Connection:
    return psycopg.connect(
        host="postgres",
        dbname="PowderAppDB",
        user="Harley",
        password="Chaotic",
        row_factory=dict_row,
    )


def truncate_tables(cur: psycopg.Cursor[Any]) -> None:
    cur.execute("TRUNCATE customer_sessions RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE job_edit_history RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE jobs RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE customer_accounts RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE customers RESTART IDENTITY CASCADE;")


def insert_customers(cur: psycopg.Cursor[Any], customers: Iterable[SampleCustomer]) -> None:
    for customer in customers:
        password_hash = generate_password_hash(customer.password)
        cur.execute(
            """
            INSERT INTO customer_accounts
                (email, password_hash, first_name, last_name, company_name, phone, address, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            (
                customer.email,
                password_hash,
                customer.first_name,
                customer.last_name,
                customer.company_name,
                customer.phone,
                customer.address,
                customer.created_at,
                customer.created_at,
            ),
        )
        customer_id = cur.fetchone()["id"]

        cur.execute(
            """
            INSERT INTO customers (company, contact_name, phone, email, address, notes, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,'',%s,%s)
            """,
            (
                customer.company_name,
                customer.full_name,
                customer.phone,
                customer.email,
                customer.address,
                customer.created_at,
                customer.created_at,
            ),
        )

        for job in customer.jobs:
            cur.execute(
                """
                INSERT INTO jobs
                    (created_at, date_in, due_by, contact_name, company, phone, email, po, type, priority,
                     blast, prep, color, color_source, description, notes, status, department,
                     customer_account_id, submitted_by_customer, requires_approval, customer_notes, shop_notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s)
                """,
                (
                    job.created_at,
                    job.date_in,
                    job.due_by,
                    customer.full_name,
                    customer.company_name,
                    customer.phone,
                    customer.email,
                    job.po,
                    job.job_type,
                    job.priority,
                    job.blast,
                    job.prep,
                    job.color,
                    job.color_source,
                    job.description,
                    job.notes,
                    job.status,
                    job.department,
                    customer_id,
                    job.submitted_by_customer,
                    job.requires_approval,
                    job.customer_notes,
                    job.shop_notes,
                ),
            )


def main() -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            truncate_tables(cur)
            insert_customers(cur, CUSTOMERS)
        conn.commit()

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM customer_accounts")
            account_count = cur.fetchone()["count"]
            cur.execute("SELECT COUNT(*) AS count FROM jobs")
            job_count = cur.fetchone()["count"]

    print(f"Seed complete: {account_count} customer accounts, {job_count} jobs")


if __name__ == "__main__":
    main()

