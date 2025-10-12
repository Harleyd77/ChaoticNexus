"""Domain services for job intake and creation."""

from __future__ import annotations

from datetime import datetime

from app.models import Customer, Job
from app.repositories import session_scope


class JobIntakeService:
    def create_production_job(
        self,
        *,
        contact_name: str,
        company: str,
        phone: str | None,
        email: str | None,
        description: str,
        notes: str | None,
    ) -> Job:
        if not contact_name.strip():
            raise ValueError("Contact name is required")
        if not company.strip():
            raise ValueError("Company is required")
        if not description.strip():
            raise ValueError("Job description is required")

        with session_scope() as session:
            customer = self._get_or_create_customer(session, company, contact_name, phone, email)

            job = Job(
                created_at=datetime.utcnow(),
                company=company,
                contact_name=contact_name,
                phone=phone,
                email=email,
                description=description,
                notes=notes,
                status="Intake",
                department="intake",
                customer=customer,
            )
            session.add(job)
            session.flush()
            return job

    def create_railing_job(
        self,
        *,
        contact_name: str,
        company: str,
        description: str,
        measurements: str | None,
    ) -> Job:
        if not contact_name.strip():
            raise ValueError("Contact name is required")
        if not company.strip():
            raise ValueError("Company is required")
        if not description.strip():
            raise ValueError("Railing description is required")

        with session_scope() as session:
            customer = self._get_or_create_customer(session, company, contact_name, None, None)

            job = Job(
                created_at=datetime.utcnow(),
                company=company,
                contact_name=contact_name,
                description=description,
                notes=measurements,
                status="Intake",
                department="intake",
                type="Railing",
                customer=customer,
            )
            session.add(job)
            session.flush()
            return job

    def _get_or_create_customer(
        self,
        session,
        company: str,
        contact_name: str,
        phone: str | None,
        email: str | None,
    ) -> Customer:
        customer = session.query(Customer).filter(Customer.company == company).one_or_none()
        if customer:
            return customer

        customer = Customer(
            company=company,
            contact_name=contact_name,
            phone=phone,
            email=email,
            status="Active",
        )
        session.add(customer)
        session.flush()
        return customer


job_intake_service = JobIntakeService()
