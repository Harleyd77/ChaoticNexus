"""Simple key-value application settings."""

from __future__ import annotations

from sqlalchemy import Column, String, Text

from .base import BaseModel


class Setting(BaseModel):
    __tablename__ = "settings"
    __repr_attrs__ = ("id", "name")

    name = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
