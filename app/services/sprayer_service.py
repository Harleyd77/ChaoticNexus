"""Sprayer service orchestrating batches and job timing."""

from __future__ import annotations

from app.repositories.sprayer import sprayer_repo


class SprayerService:
    def __init__(self, repository=sprayer_repo):
        self._repo = repository

    def dashboard(self):
        powders = self._repo.list_powders()
        open_batches = self._repo.list_open_batches()
        recent = self._repo.list_recent_batches()
        return powders, open_batches, recent

    def start_batch(
        self,
        *,
        powder_id: int,
        role: str | None,
        operator: str | None,
        note: str | None,
        start_weight_kg: float,
    ):
        return self._repo.create_batch(
            powder_id=powder_id,
            role=role,
            operator=operator,
            note=note,
            start_weight_kg=start_weight_kg,
        )

    def batch_detail(self, batch_id: int):
        batch = self._repo.get_batch(batch_id)
        jobs = self._repo.list_batch_jobs(batch_id)
        return batch, jobs

    def attach_job(self, batch_id: int, job_id: int):
        self._repo.attach_job(batch_id, job_id)

    def remove_job(self, batch_id: int, job_id: int):
        self._repo.remove_job(batch_id, job_id)

    def start_job(self, batch_id: int, job_id: int):
        self._repo.start_job(batch_id, job_id)

    def end_job(self, batch_id: int, job_id: int):
        self._repo.end_job(batch_id, job_id)

    def close_batch(self, batch_id: int, *, end_weight_kg: float):
        self._repo.close_batch(batch_id, end_weight_kg=end_weight_kg)


sprayer_service = SprayerService()
