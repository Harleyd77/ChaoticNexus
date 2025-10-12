"""Customer portal data service layer."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models import CustomerAccount, Job
from app.repositories import session_scope


@dataclass
class CustomerDashboardStats:
    total: int
    pending: int
    completed: int
    overdue: int


class CustomerPortalService:
    """Helpers for customer portal dashboard, jobs, and profile data."""

    def get_account_with_customer(self, account_id: int) -> CustomerAccount | None:
        with session_scope() as session:
            return (
                session.execute(
                    select(CustomerAccount)
                    .options(selectinload(CustomerAccount.customer))
                    .filter(CustomerAccount.id == account_id)
                )
                .scalars()
                .one_or_none()
            )

    def list_jobs_for_account(
        self,
        account_id: int,
        *,
        search: str | None = None,
        status: str | None = None,
    ) -> Iterable[Job]:
        stmt = (
            select(Job)
            .options(
                selectinload(Job.powder_usage),
                selectinload(Job.time_logs),
            )
            .filter(Job.customer_account_id == account_id)
            .order_by(Job.created_at.desc())
        )
        if search:
            like = f"%{search}%"
            stmt = stmt.filter(Job.description.ilike(like) | Job.po.ilike(like))
        if status:
            stmt = stmt.filter(Job.status == status)

        with session_scope() as session:
            return session.execute(stmt).scalars().all()

    def get_job(self, account_id: int, job_id: int) -> Job | None:
        with session_scope() as session:
            return (
                session.execute(
                    select(Job)
                    .options(
                        selectinload(Job.powder_usage),
                        selectinload(Job.time_logs),
                    )
                    .filter(Job.customer_account_id == account_id, Job.id == job_id)
                )
                .scalars()
                .one_or_none()
            )

    def dashboard_stats(self, account_id: int) -> CustomerDashboardStats:
        today = date.today()
        with session_scope() as session:
            total = session.execute(
                select(func.count()).filter(Job.customer_account_id == account_id)
            ).scalar_one()

            pending = session.execute(
                select(func.count()).filter(
                    Job.customer_account_id == account_id,
                    Job.status.in_(["In Progress", "Not Started", "Pending Approval"]),
                )
            ).scalar_one()

            completed = session.execute(
                select(func.count()).filter(
                    Job.customer_account_id == account_id,
                    Job.status == "Completed",
                )
            ).scalar_one()

            overdue = session.execute(
                select(func.count()).filter(
                    Job.customer_account_id == account_id,
                    Job.due_by.isnot(None),
                    Job.due_by < today,
                    Job.status != "Completed",
                )
            ).scalar_one()

        return CustomerDashboardStats(
            total=total or 0,
            pending=pending or 0,
            completed=completed or 0,
            overdue=overdue or 0,
        )

    def update_account(self, account_id: int, **fields) -> CustomerAccount | None:
        with session_scope() as session:
            account = session.get(CustomerAccount, account_id)
            if not account:
                return None

            for key, value in fields.items():
                if hasattr(account, key):
                    setattr(account, key, value)

            session.flush()
            return account

    def create_customer_job(self, account_id: int, **fields) -> Job:
        with session_scope() as session:
            account = session.get(CustomerAccount, account_id)
            if not account:
                raise ValueError("Customer account not found")

            job = Job(
                customer_account_id=account_id,
                company=fields.get("company") or account.company_name,
                contact_name=fields.get("contact_name")
                or f"{account.first_name} {account.last_name}",
                phone=fields.get("phone") or account.phone,
                email=fields.get("email") or account.email,
                po=fields.get("po"),
                type=fields.get("type"),
                priority=fields.get("priority"),
                blast=fields.get("blast"),
                prep=fields.get("prep"),
                color=fields.get("color"),
                description=fields.get("description"),
                notes=fields.get("notes"),
                due_by=fields.get("due_by"),
                status="Pending Approval",
                department="intake",
                submitted_by_customer=True,
            )
            session.add(job)
            session.flush()
            return job

    def update_customer_job(self, account_id: int, job_id: int, **fields) -> Job | None:
        with session_scope() as session:
            job = (
                session.query(Job)
                .filter(Job.customer_account_id == account_id, Job.id == job_id)
                .one_or_none()
            )
            if not job:
                return None

            editable_fields = {
                "contact_name",
                "phone",
                "email",
                "po",
                "type",
                "priority",
                "blast",
                "prep",
                "color",
                "description",
                "notes",
                "due_by",
            }
            for key, value in fields.items():
                if key in editable_fields:
                    setattr(job, key, value)

            session.flush()
            return job


customer_portal_service = CustomerPortalService()
