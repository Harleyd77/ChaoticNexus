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
        date_in: str | None = None,
        due_by: str | None = None,
        po: str | None = None,
        category: str | None = None,
        blast: str | None = None,
        priority: str | None = None,
        prep: str | None = None,
        color: str | None = None,
        color_source: str | None = None,
        intake_source: str | None = None,
    ) -> Job:
        if not contact_name.strip():
            raise ValueError("Contact name is required")
        if not company.strip():
            raise ValueError("Company is required")
        if not description.strip():
            raise ValueError("Job description is required")

        with session_scope() as session:
            customer = self._get_or_create_customer(session, company, contact_name, phone, email)

            # Parse dates
            parsed_date_in = None
            parsed_due_by = None
            if date_in:
                try:
                    parsed_date_in = datetime.fromisoformat(date_in).date()
                except ValueError:
                    parsed_date_in = None
            if due_by:
                try:
                    parsed_due_by = datetime.fromisoformat(due_by).date()
                except ValueError:
                    parsed_due_by = None

            job = Job(
                created_at=datetime.utcnow(),
                date_in=parsed_date_in,
                due_by=parsed_due_by,
                company=company,
                contact_name=contact_name,
                phone=phone,
                email=email,
                po=po,
                type=category,
                priority=priority,
                blast=blast,
                prep=prep,
                color=color,
                color_source=color_source,
                description=description,
                notes=notes,
                status="Intake",
                department="intake",
                intake_source=intake_source,
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
