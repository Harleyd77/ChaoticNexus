"""Job repository for operations on job entities."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select

from ..models import Job
from .session import session_scope


class JobRepository:
    def list_jobs(self, *, query: str | None = None) -> Iterable[Job]:
        stmt = select(Job).order_by(Job.id.desc())
        if query:
            like = f"%{query}%"
            stmt = stmt.filter(Job.company.ilike(like) | Job.description.ilike(like))

        with session_scope() as session:
            return session.execute(stmt).scalars().all()

    def get_job(self, job_id: int) -> Job | None:
        with session_scope() as session:
            return session.get(Job, job_id)


job_repo = JobRepository()
