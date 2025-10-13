"""Customer repository for data access."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select

from ..models import Contact, Customer, CustomerAccount
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

    def search_customers(self, query: str) -> list[Customer]:
        like = f"%{query}%"
        with session_scope() as session:
            stmt = (
                select(Customer)
                .filter(
                    Customer.company.ilike(like)
                    | Customer.contact_name.ilike(like)
                    | Customer.email.ilike(like)
                    | Customer.phone.ilike(like)
                )
                .order_by(Customer.company)
            )
            return session.execute(stmt).scalars().all()

    # Customer portal accounts (admin side)
    def list_accounts(self, customer_id: int | None = None) -> list[CustomerAccount]:
        with session_scope() as session:
            stmt = select(CustomerAccount).order_by(CustomerAccount.email)
            if customer_id:
                stmt = stmt.filter(CustomerAccount.customer_id == customer_id)
            return session.execute(stmt).scalars().all()

    def create_account(
        self,
        *,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        customer_id: int | None = None,
        company_name: str | None = None,
        phone: str | None = None,
    ) -> CustomerAccount:
        with session_scope() as session:
            acct = CustomerAccount(
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                customer_id=customer_id,
                company_name=company_name,
                phone=phone,
                email_verified=False,
                is_active=True,
            )
            session.add(acct)
            session.flush()
            return acct

    def set_account_active(self, account_id: int, *, is_active: bool) -> bool:
        with session_scope() as session:
            acct = session.get(CustomerAccount, account_id)
            if not acct:
                return False
            acct.is_active = is_active
            session.flush()
            return True

    # Contacts CRUD
    def list_contacts(self, customer_id: int) -> list[Contact]:
        with session_scope() as session:
            return (
                session.execute(select(Contact).filter(Contact.customer_id == customer_id))
                .scalars()
                .all()
            )

    def add_contact(
        self, customer_id: int, *, name: str, phone: str | None, email: str | None
    ) -> Contact:
        with session_scope() as session:
            contact = Contact(customer_id=customer_id, name=name, phone=phone, email=email)
            session.add(contact)
            session.flush()
            return contact

    def update_contact(self, customer_id: int, contact_id: int, **fields) -> Contact | None:
        with session_scope() as session:
            contact = session.get(Contact, contact_id)
            if not contact or contact.customer_id != customer_id:
                return None
            for key, value in fields.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
            session.flush()
            return contact

    def delete_contact(self, customer_id: int, contact_id: int) -> bool:
        with session_scope() as session:
            contact = session.get(Contact, contact_id)
            if not contact or contact.customer_id != customer_id:
                return False
            session.delete(contact)
            session.flush()
            return True


customer_repo = CustomerRepository()
