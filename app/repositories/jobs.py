"""Job repository for operations on job entities."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import Customer, Job, JobPhoto, JobPowder, PowderUsage, TimeLog
from .session import session_scope


class JobRepository:
    def list_jobs(self, *, query: str | None = None) -> Iterable[Job]:
        stmt = select(Job).options(selectinload(Job.customer)).order_by(Job.id.desc())
        if query:
            like = f"%{query}%"
            stmt = stmt.filter(Job.company.ilike(like) | Job.description.ilike(like))

        with session_scope() as session:
            return session.execute(stmt).scalars().all()

    def create_job(
        self,
        *,
        company: str,
        contact_name: str | None,
        description: str,
        customer_id: int | None = None,
    ) -> Job:
        if not company.strip():
            raise ValueError("Company name is required")
        if not description.strip():
            raise ValueError("Description is required")

        with session_scope() as session:
            customer = None
            if customer_id:
                customer = session.get(Customer, customer_id)
            elif company:
                customer = session.query(Customer).filter(Customer.company.ilike(company)).first()

            job = Job(
                created_at=datetime.utcnow(),
                company=company,
                contact_name=contact_name,
                description=description,
                status="Intake",
                department="intake",
                customer=customer,
            )
            session.add(job)
            session.flush()
            return job

    def update_job(self, job_id: int, **fields) -> Job | None:
        allowed_fields = {
            "contact_name",
            "phone",
            "email",
            "po",
            "type",
            "priority",
            "blast",
            "prep",
            "color",
            "status",
            "department",
            "date_in",
            "due_by",
            "description",
            "notes",
        }

        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return None

            for key, value in fields.items():
                if key in allowed_fields:
                    setattr(job, key, value)

            session.flush()
            return job

    def get_job(self, job_id: int) -> Job | None:
        with session_scope() as session:
            return session.execute(
                select(Job)
                .options(
                    selectinload(Job.customer),
                    selectinload(Job.customer_account),
                    selectinload(Job.time_logs),
                    selectinload(Job.job_powders).selectinload(JobPowder.powder),
                    selectinload(Job.powder_usage).selectinload(PowderUsage.powder),
                )
                .filter(Job.id == job_id)
            ).scalar_one_or_none()

    def list_time_logs(self, job_id: int) -> Iterable[TimeLog]:
        with session_scope() as session:
            return (
                session.execute(
                    select(TimeLog)
                    .filter(TimeLog.job_id == job_id)
                    .order_by(TimeLog.start_ts.desc())
                )
                .scalars()
                .all()
            )

    def list_powder_usage(self, job_id: int) -> Iterable[PowderUsage]:
        with session_scope() as session:
            return (
                session.execute(
                    select(PowderUsage)
                    .options(selectinload(PowderUsage.powder))
                    .filter(PowderUsage.job_id == job_id)
                    .order_by(PowderUsage.created_at.desc())
                )
                .scalars()
                .all()
            )

    # Photos
    def list_photos(self, job_id: int) -> Iterable[JobPhoto]:
        with session_scope() as session:
            return (
                session.execute(select(JobPhoto).filter(JobPhoto.job_id == job_id)).scalars().all()
            )

    def add_photo(self, job_id: int, *, filename: str, original_name: str | None) -> JobPhoto:
        with session_scope() as session:
            photo = JobPhoto(job_id=job_id, filename=filename, original_name=original_name)
            session.add(photo)
            session.flush()
            return photo

    def delete_photo(self, job_id: int, photo_id: int) -> bool:
        with session_scope() as session:
            photo = session.get(JobPhoto, photo_id)
            if not photo or photo.job_id != job_id:
                return False
            session.delete(photo)
            session.flush()
            return True

    # Screen / ordering
    def set_on_screen(self, job_id: int, *, on_screen: bool) -> bool:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return False
            job.on_screen = on_screen
            session.flush()
            return True

    def set_screen_order(self, job_id: int, *, order_index: int | None) -> bool:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return False
            job.screen_order_index = order_index
            session.flush()
            return True

    def reorder_screen(self, job_ids_in_order: list[int]) -> None:
        with session_scope() as session:
            for index, job_id in enumerate(job_ids_in_order):
                job = session.get(Job, job_id)
                if job:
                    job.on_screen = True
                    job.screen_order_index = index
            session.flush()

    # Status and lifecycle
    def archive_job(self, job_id: int, *, reason: str | None = None) -> bool:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return False
            job.archived = True
            job.archived_reason = reason
            session.flush()
            return True

    def unarchive_job(self, job_id: int) -> bool:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return False
            job.archived = False
            session.flush()
            return True

    def complete_job(self, job_id: int, *, completed_at: datetime | None = None) -> bool:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return False
            job.status = "Completed"
            job.department = "completed"
            job.completed_at = completed_at or datetime.utcnow()
            session.flush()
            return True

    def reopen_job(self, job_id: int) -> bool:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return False
            job.status = "In Progress"
            job.department = "intake"
            job.completed_at = None
            session.flush()
            return True

    def delete_job(self, job_id: int) -> bool:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return False
            session.delete(job)
            session.flush()
            return True


job_repo = JobRepository()
