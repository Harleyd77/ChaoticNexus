"""Reusable SQLAlchemy mixins used across models."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, func


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` timestamps."""

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    """Adds a ``deleted_at`` column for soft deletion semantics."""

    deleted_at = Column(DateTime(timezone=True), nullable=True)


class ReprMixin:
    """Provide a helpful default ``__repr__`` implementation."""

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        cls = self.__class__.__name__
        attrs = []
        for key in getattr(self, "__repr_attrs__", ("id",)):
            value = getattr(self, key, None)
            attrs.append(f"{key}={value!r}")
        joined = " ".join(attrs)
        return f"<{cls} {joined}>"
