"""Print template model for JSON-driven templates."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, String, Text

from .base import BaseModel
from .mixins import TimestampMixin


class PrintTemplate(BaseModel, TimestampMixin):
    __tablename__ = "print_templates"
    __repr_attrs__ = ("id", "template_type", "name", "is_default")

    template_type = Column(String(120), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_default = Column(Boolean, nullable=False, server_default="0")
