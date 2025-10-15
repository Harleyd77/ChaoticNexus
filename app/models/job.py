"""Job and related operational models."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from .mixins import SoftDeleteMixin, TimestampMixin


class Job(BaseModel, TimestampMixin, SoftDeleteMixin):
    """Represents a powder coating job."""

    __tablename__ = "jobs"
    __repr_attrs__ = ("id", "company", "status")

    date_in = Column(Date, nullable=True)
    due_by = Column(Date, nullable=True)
    contact_name = Column(String(255), nullable=True)
    company = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    po = Column(String(120), nullable=True)
    type = Column(String(120), nullable=True)
    intake_source = Column(String(120), nullable=True)
    priority = Column(String(60), nullable=True)
    blast = Column(String(120), nullable=True)
    prep = Column(String(120), nullable=True)
    color = Column(String(120), nullable=True)
    color_source = Column(String(120), nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(60), nullable=False, index=True)
    department = Column(String(60), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    work_order_json = Column(JSON, nullable=True)
    archived = Column(Boolean, nullable=False, server_default="0")
    archived_reason = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=True)
    on_screen = Column(Boolean, nullable=False, server_default="0")
    screen_order_index = Column(Integer, nullable=True)
    submitted_by_customer = Column(Boolean, nullable=False, server_default="0")
    requires_approval = Column(Boolean, nullable=False, server_default="0")
    customer_notes = Column(Text, nullable=True)
    shop_notes = Column(Text, nullable=True)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_account_id = Column(Integer, ForeignKey("customer_accounts.id"), nullable=True)

    customer = relationship("Customer", back_populates="jobs")
    customer_account = relationship("CustomerAccount", back_populates="jobs")
    time_logs = relationship("TimeLog", back_populates="job", cascade="all, delete-orphan")
    photos = relationship("JobPhoto", back_populates="job", cascade="all, delete-orphan")
    edit_history = relationship(
        "JobEditHistory", back_populates="job", cascade="all, delete-orphan"
    )
    job_powders = relationship("JobPowder", back_populates="job", cascade="all, delete-orphan")
    powder_usage = relationship("PowderUsage", back_populates="job", cascade="all, delete-orphan")


class TimeLog(BaseModel, TimestampMixin):
    __tablename__ = "time_logs"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    department = Column(String(120), nullable=False)
    start_ts = Column(DateTime(timezone=True), nullable=False)
    end_ts = Column(DateTime(timezone=True), nullable=True)
    minutes = Column(Integer, nullable=True)

    job = relationship("Job", back_populates="time_logs")


class JobPhoto(BaseModel, TimestampMixin):
    __tablename__ = "job_photos"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=True)

    job = relationship("Job", back_populates="photos")


class JobEditHistory(BaseModel, TimestampMixin):
    __tablename__ = "job_edit_history"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(
        Integer, ForeignKey("customer_accounts.id", ondelete="SET NULL"), nullable=True
    )
    field_name = Column(String(120), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_reason = Column(Text, nullable=True)
    changed_by_customer = Column(Boolean, nullable=False, server_default="1")

    job = relationship("Job", back_populates="edit_history")
    customer_account = relationship("CustomerAccount", back_populates="edit_history")
