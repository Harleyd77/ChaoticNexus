"""Authentication services for admin and customer accounts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError

try:  # pragma: no cover - optional dependency
    from passlib.hash import pbkdf2_sha256
except ImportError:  # pragma: no cover - optional dependency fallback
    pbkdf2_sha256 = None  # type: ignore

from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Customer, CustomerAccount, User
from app.repositories import session_scope


def _hash_password(password: str) -> str:
    if pbkdf2_sha256:
        return pbkdf2_sha256.hash(password)
    return generate_password_hash(password)


def _verify_password(stored_hash: str, password: str) -> bool:
    if pbkdf2_sha256 and pbkdf2_sha256.identify(stored_hash):  # pragma: no cover
        return pbkdf2_sha256.verify(password, stored_hash)
    return check_password_hash(stored_hash, password)


@dataclass
class CustomerAuthResult:
    account: CustomerAccount
    customer: Customer | None


class CustomerAuthService:
    """Handle registration and login for the customer portal."""

    def register_customer_account(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        company_name: str | None = None,
        phone: str | None = None,
    ) -> CustomerAccount:
        if not email or "@" not in email:
            raise ValueError("A valid email address is required")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not first_name.strip():
            raise ValueError("First name is required")
        if not last_name.strip():
            raise ValueError("Last name is required")

        password_hash = _hash_password(password)

        with session_scope() as session:
            account = CustomerAccount(
                email=email.lower(),
                password_hash=password_hash,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                company_name=company_name.strip() if company_name else None,
                phone=phone.strip() if phone else None,
                email_verified=False,
            )
            session.add(account)

            if company_name:
                existing_customer = (
                    session.query(Customer)
                    .filter(Customer.company.ilike(company_name.strip()))
                    .one_or_none()
                )
                if existing_customer:
                    account.customer_id = existing_customer.id

            try:
                session.flush()
            except IntegrityError as exc:
                session.rollback()
                if "email" in str(exc.orig).lower():
                    raise ValueError("An account with this email already exists") from exc
                raise

            return account

    def authenticate_customer(self, *, email: str, password: str) -> CustomerAuthResult | None:
        if not email or not password:
            return None

        with session_scope() as session:
            account = (
                session.query(CustomerAccount)
                .filter(CustomerAccount.email == email.lower())
                .one_or_none()
            )
            if not account or not _verify_password(account.password_hash, password):
                return None

            account.last_login = datetime.utcnow()
            session.flush()
            customer = account.customer
            return CustomerAuthResult(account=account, customer=customer)


customer_auth_service = CustomerAuthService()


class AdminAuthService:
    """Handle authentication for admin/back-office users."""

    def authenticate_admin(self, *, username: str, password: str) -> User | None:
        if not username or not password:
            return None
        with session_scope() as session:
            user = session.query(User).filter(User.username == username).one_or_none()
            if not user or not _verify_password(user.password_hash, password):
                return None
            return user


admin_auth_service = AdminAuthService()
