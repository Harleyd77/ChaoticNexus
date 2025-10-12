"""Job repository for operations on job entities."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import Job, JobPowder, PowderUsage, TimeLog
from .session import session_scope


class JobRepository:
    def list_jobs(self, *, query: str | None = None) -> Iterable[Job]:
        stmt = select(Job).options(selectinload(Job.customer)).order_by(Job.id.desc())
        if query:
            like = f"%{query}%"
            stmt = stmt.filter(Job.company.ilike(like) | Job.description.ilike(like))

        with session_scope() as session:
            return session.execute(stmt).scalars().all()

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


job_repo = JobRepository()
