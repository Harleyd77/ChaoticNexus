"""Sprayer-related models: batches and batch jobs."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from .mixins import TimestampMixin


class SprayBatch(BaseModel, TimestampMixin):
    __tablename__ = "spray_batch"

    powder_id = Column(Integer, ForeignKey("powders.id", ondelete="RESTRICT"), nullable=False)
    role = Column(String(50), nullable=True)
    operator = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    start_weight_kg = Column(Numeric(10, 2), nullable=False)
    end_weight_kg = Column(Numeric(10, 2), nullable=True)
    used_kg = Column(Numeric(10, 2), nullable=True)
    duration_min = Column(Numeric(10, 2), nullable=True)

    powder = relationship("Powder")
    jobs = relationship("SprayBatchJob", back_populates="batch", cascade="all, delete-orphan")


class SprayBatchJob(BaseModel, TimestampMixin):
    __tablename__ = "spray_batch_jobs"

    batch_id = Column(Integer, ForeignKey("spray_batch.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    time_min = Column(Numeric(10, 2), nullable=True)
    start_ts = Column(DateTime(timezone=True), nullable=True)
    end_ts = Column(DateTime(timezone=True), nullable=True)
    elapsed_seconds = Column(Numeric(12, 3), nullable=True)
    running_since = Column(DateTime(timezone=True), nullable=True)

    batch = relationship("SprayBatch", back_populates="jobs")
    job = relationship("Job")
