"""User account models."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import JSONB

from .base import BaseModel
from .mixins import TimestampMixin


class User(BaseModel, TimestampMixin):
    """Administrative user that can access the back office UI."""

    __tablename__ = "users"
    __repr_attrs__ = ("id", "username", "is_admin")

    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    permissions_json = Column(JSONB, nullable=True)
