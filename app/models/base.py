"""Shared SQLAlchemy model base classes."""

from __future__ import annotations

from ..extensions import db
from .mixins import ReprMixin


class BaseModel(db.Model, ReprMixin):
    """Abstract base model that provides an integer primary key and repr."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
