"""Customer portal data service layer."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import CustomerAccount, Job
from app.repositories import session_scope


@dataclass
class CustomerDashboardStats:
    total: int
    pending: int
    completed: int
    overdue: int
    last_login: str | None
    member_since: str | None


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

    def list_recent_jobs(self, account_id: int, limit: int = 5) -> Iterable[Job]:
        stmt = (
            select(Job)
            .options(
                selectinload(Job.customer),
                selectinload(Job.time_logs),
                selectinload(Job.powder_usage),
            )
            .filter(Job.customer_account_id == account_id)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
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
            jobs = (
                session.execute(select(Job).filter(Job.customer_account_id == account_id))
                .scalars()
                .all()
            )
            account = session.get(CustomerAccount, account_id)

        total = len(jobs)
        completed = sum(1 for job in jobs if job.status == "Completed")
        overdue = sum(
            1 for job in jobs if job.due_by and job.due_by < today and job.status != "Completed"
        )

        last_login = None
        member_since = None
        if account and account.last_login:
            last_login = account.last_login.strftime("%Y-%m-%d")
        if account and account.created_at:
            member_since = account.created_at.strftime("%Y-%m-%d")

        return CustomerDashboardStats(
            total=total,
            pending=sum(
                1
                for job in jobs
                if job.status
                in [
                    "In Progress",
                    "Not Started",
                    "Pending Approval",
                    "Ready for Pickup",
                ]
            ),
            completed=completed,
            overdue=overdue,
            last_login=last_login,
            member_since=member_since,
        )

    def customer_summary(self, account_id: int) -> dict[str, int]:
        jobs = self.list_jobs_for_account(account_id)
        total = len(jobs)
        completed = sum(1 for job in jobs if job.status == "Completed")
        in_progress = sum(
            1
            for job in jobs
            if job.status
            in [
                "In Progress",
                "Not Started",
                "Pending Approval",
                "Ready for Pickup",
            ]
        )
        pending_approval = sum(1 for job in jobs if job.status == "Pending Approval")
        ready_for_pickup = sum(1 for job in jobs if job.status == "Ready for Pickup")

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending_approval": pending_approval,
            "ready_for_pickup": ready_for_pickup,
        }

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
