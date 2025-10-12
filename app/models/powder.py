"""Powder inventory related models."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from .mixins import TimestampMixin


class Powder(BaseModel, TimestampMixin):
    __tablename__ = "powders"
    __repr_attrs__ = ("id", "powder_color", "manufacturer")

    powder_color = Column(String(255), nullable=False, index=True)
    manufacturer = Column(String(255), nullable=True)
    product_code = Column(String(120), nullable=True)
    gloss_level = Column(String(120), nullable=True)
    finish = Column(String(120), nullable=True)
    metallic = Column(Integer, nullable=True)
    needs_clear = Column(Integer, nullable=True)
    int_ext = Column(String(120), nullable=True)
    additional_code = Column(String(120), nullable=True)
    msds_url = Column(Text, nullable=True)
    sds_url = Column(Text, nullable=True)
    web_link = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    additional_info = Column(Text, nullable=True)
    cure_schedule = Column(Text, nullable=True)
    price_per_kg = Column(Numeric(10, 2), nullable=True)
    charge_per_lb = Column(Numeric(10, 2), nullable=True)
    weight_box_kg = Column(Numeric(10, 2), nullable=True)
    last_price_check = Column(DateTime(timezone=True), nullable=True)
    in_stock = Column(Numeric(10, 2), nullable=True)
    shipping_cost = Column(Numeric(10, 2), nullable=True)
    picture_url = Column(Text, nullable=True)
    color_family = Column(String(120), nullable=True)
    aliases = Column(Text, nullable=True)
    on_hand_kg = Column(Numeric(10, 2), nullable=True)
    last_weighed_kg = Column(Numeric(10, 2), nullable=True)
    last_weighed_at = Column(DateTime(timezone=True), nullable=True)

    job_powders = relationship("JobPowder", back_populates="powder", cascade="all, delete-orphan")
    inventory_logs = relationship(
        "InventoryLog", back_populates="powder", cascade="all, delete-orphan"
    )
    reorder_settings = relationship(
        "ReorderSetting", back_populates="powder", cascade="all, delete-orphan"
    )
    powder_usage = relationship(
        "PowderUsage", back_populates="powder", cascade="all, delete-orphan"
    )


class JobPowder(BaseModel, TimestampMixin):
    __tablename__ = "job_powders"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    powder_id = Column(Integer, ForeignKey("powders.id", ondelete="SET NULL"), nullable=True)
    powder_color = Column(String(255), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    quantity_used = Column(Numeric(10, 2), nullable=True)
    notes = Column(Text, nullable=True)

    job = relationship("Job", back_populates="job_powders")
    powder = relationship("Powder", back_populates="job_powders")


class InventoryLog(BaseModel, TimestampMixin):
    __tablename__ = "inventory_log"
    __repr_attrs__ = ("id", "powder_id", "change_type")

    powder_id = Column(Integer, ForeignKey("powders.id", ondelete="CASCADE"), nullable=False)
    change_type = Column(String(120), nullable=False)
    old_value = Column(Numeric(10, 2), nullable=True)
    new_value = Column(Numeric(10, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)

    powder = relationship("Powder", back_populates="inventory_logs")


class ReorderSetting(BaseModel, TimestampMixin):
    __tablename__ = "reorder_settings"

    powder_id = Column(Integer, ForeignKey("powders.id", ondelete="CASCADE"), nullable=True)
    low_stock_threshold = Column(Numeric(10, 2), nullable=True)
    reorder_quantity = Column(Numeric(10, 2), nullable=True)
    supplier_info = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    powder = relationship("Powder", back_populates="reorder_settings")


class PowderUsage(BaseModel, TimestampMixin):
    __tablename__ = "powder_usage"

    powder_id = Column(Integer, ForeignKey("powders.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    amount_used = Column(Numeric(10, 2), nullable=True)
    notes = Column(Text, nullable=True)

    powder = relationship("Powder", back_populates="powder_usage")
    job = relationship("Job", back_populates="powder_usage")
