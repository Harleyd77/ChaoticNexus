"""Sprayer repository for batches and batch jobs."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from sqlalchemy import select

from ..models import Job, Powder, SprayBatch, SprayBatchJob
from .session import session_scope


class SprayerRepository:
    def list_powders(self) -> Iterable[Powder]:
        with session_scope() as session:
            return session.execute(select(Powder).order_by(Powder.powder_color)).scalars().all()

    def list_open_batches(self) -> Iterable[SprayBatch]:
        with session_scope() as session:
            return (
                session.execute(
                    select(SprayBatch)
                    .filter(SprayBatch.ended_at.is_(None))
                    .order_by(SprayBatch.created_at.desc())
                )
                .scalars()
                .all()
            )

    def list_recent_batches(self, limit: int = 20) -> Iterable[SprayBatch]:
        with session_scope() as session:
            return (
                session.execute(
                    select(SprayBatch)
                    .filter(SprayBatch.ended_at.isnot(None))
                    .order_by(SprayBatch.ended_at.desc())
                    .limit(limit)
                )
                .scalars()
                .all()
            )

    def create_batch(
        self,
        *,
        powder_id: int,
        role: str | None,
        operator: str | None,
        note: str | None,
        start_weight_kg: float,
    ) -> SprayBatch:
        with session_scope() as session:
            batch = SprayBatch(
                powder_id=powder_id,
                role=role,
                operator=operator,
                note=note,
                start_weight_kg=start_weight_kg,
                started_at=datetime.utcnow(),
            )
            session.add(batch)
            session.flush()
            return batch

    def get_batch(self, batch_id: int) -> SprayBatch | None:
        with session_scope() as session:
            return session.get(SprayBatch, batch_id)

    def list_batch_jobs(self, batch_id: int) -> Iterable[SprayBatchJob]:
        with session_scope() as session:
            return (
                session.execute(select(SprayBatchJob).filter(SprayBatchJob.batch_id == batch_id))
                .scalars()
                .all()
            )

    def attach_job(self, batch_id: int, job_id: int) -> None:
        with session_scope() as session:
            if not session.get(SprayBatch, batch_id):
                return
            if not session.get(Job, job_id):
                return
            existing = (
                session.execute(
                    select(SprayBatchJob).filter(
                        SprayBatchJob.batch_id == batch_id, SprayBatchJob.job_id == job_id
                    )
                )
                .scalars()
                .one_or_none()
            )
            if existing:
                return
            session.add(SprayBatchJob(batch_id=batch_id, job_id=job_id))
            session.flush()

    def remove_job(self, batch_id: int, job_id: int) -> None:
        with session_scope() as session:
            row = (
                session.execute(
                    select(SprayBatchJob).filter(
                        SprayBatchJob.batch_id == batch_id, SprayBatchJob.job_id == job_id
                    )
                )
                .scalars()
                .one_or_none()
            )
            if row:
                session.delete(row)
                session.flush()

    def start_job(self, batch_id: int, job_id: int) -> None:
        with session_scope() as session:
            row = (
                session.execute(
                    select(SprayBatchJob).filter(
                        SprayBatchJob.batch_id == batch_id, SprayBatchJob.job_id == job_id
                    )
                )
                .scalars()
                .one_or_none()
            )
            if not row:
                row = SprayBatchJob(batch_id=batch_id, job_id=job_id)
                session.add(row)
            now = datetime.utcnow()
            if row.start_ts is None:
                row.start_ts = now
            if row.running_since is None and row.end_ts is None:
                row.running_since = now
            session.flush()

    def end_job(self, batch_id: int, job_id: int) -> None:
        with session_scope() as session:
            row = (
                session.execute(
                    select(SprayBatchJob).filter(
                        SprayBatchJob.batch_id == batch_id, SprayBatchJob.job_id == job_id
                    )
                )
                .scalars()
                .one_or_none()
            )
            if not row:
                return
            now = datetime.utcnow()
            if row.running_since:
                row.elapsed_seconds = (row.elapsed_seconds or 0) + max(
                    0, (now - row.running_since).total_seconds()
                )
                row.running_since = None
            if row.end_ts is None:
                row.end_ts = now
            if row.elapsed_seconds:
                row.time_min = (row.elapsed_seconds or 0) / 60.0
            session.flush()

    def close_batch(self, batch_id: int, *, end_weight_kg: float) -> None:
        with session_scope() as session:
            batch = session.get(SprayBatch, batch_id)
            if not batch or batch.ended_at:
                return
            now = datetime.utcnow()
            # finalize each job
            jobs = (
                session.execute(select(SprayBatchJob).filter(SprayBatchJob.batch_id == batch_id))
                .scalars()
                .all()
            )
            for row in jobs:
                if row.running_since:
                    row.elapsed_seconds = (row.elapsed_seconds or 0) + max(
                        0, (now - row.running_since).total_seconds()
                    )
                    row.running_since = None
                if row.end_ts is None:
                    row.end_ts = now
                if row.elapsed_seconds:
                    row.time_min = (row.elapsed_seconds or 0) / 60.0
            # finalize batch
            batch.ended_at = now
            start = batch.started_at or now
            batch.duration_min = max(0.0, (now - start).total_seconds() / 60.0)
            batch.end_weight_kg = end_weight_kg
            if batch.start_weight_kg is not None and end_weight_kg is not None:
                batch.used_kg = max(0.0, float(batch.start_weight_kg) - float(end_weight_kg))
            session.flush()


sprayer_repo = SprayerRepository()
