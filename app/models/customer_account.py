"""Customer portal account models."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from .mixins import TimestampMixin


class CustomerAccount(BaseModel, TimestampMixin):
    """Represents a customer-facing login for the portal."""

    __tablename__ = "customer_accounts"
    __repr_attrs__ = ("id", "email", "is_active")

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="1")
    email_verified = Column(Boolean, nullable=False, server_default="0")
    last_login = Column(DateTime(timezone=True), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    jobs = relationship("Job", back_populates="customer_account")
    edit_history = relationship("JobEditHistory", back_populates="customer_account")
