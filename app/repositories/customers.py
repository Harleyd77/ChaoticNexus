"""Customer repository for data access."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select

from ..models import Customer
from .session import session_scope


class CustomerRepository:
    """Encapsulate database access for customers and contacts."""

    def list_customers(self) -> Iterable[Customer]:
        with session_scope() as session:
            return session.execute(select(Customer).order_by(Customer.company)).scalars().all()

    def get_customer(self, customer_id: int) -> Customer | None:
        with session_scope() as session:
            return session.get(Customer, customer_id)

    def create_customer(self, **kwargs) -> Customer:
        with session_scope() as session:
            customer = Customer(**kwargs)
            session.add(customer)
            session.flush()
            return customer

    def update_customer(self, customer_id: int, **kwargs) -> Customer | None:
        with session_scope() as session:
            customer = session.get(Customer, customer_id)
            if not customer:
                return None
            for key, value in kwargs.items():
                setattr(customer, key, value)
            session.flush()
            return customer

    def query_by_company(self, company_name: str):
        return select(Customer).filter(Customer.company.ilike(company_name))


customer_repo = CustomerRepository()
