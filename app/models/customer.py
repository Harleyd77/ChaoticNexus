"""Customer and contact models."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel
from .mixins import TimestampMixin


class Customer(BaseModel, TimestampMixin):
    """Represents an organisation that submits jobs."""

    __tablename__ = "customers"
    __repr_attrs__ = ("id", "company")

    company = Column(String(255), nullable=False, unique=True, index=True)
    contact_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    phone_ext = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    street = Column(String(255), nullable=True)
    city = Column(String(120), nullable=True)
    region = Column(String(120), nullable=True)
    postal_code = Column(String(30), nullable=True)
    country = Column(String(120), nullable=True)
    website = Column(String(255), nullable=True)
    tax_id = Column(String(120), nullable=True)
    account_number = Column(String(120), nullable=True)
    terms = Column(String(120), nullable=True)
    status = Column(String(120), nullable=True)
    notes = Column(Text, nullable=True)

    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="customer", cascade="all, delete-orphan")


class Contact(BaseModel, TimestampMixin):
    """Additional contact attached to a customer."""

    __tablename__ = "contacts"
    __repr_attrs__ = ("id", "name", "customer_id")

    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    ext = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(120), nullable=True)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="contacts")
