"""Custom Flask CLI commands."""

from __future__ import annotations

from datetime import datetime, timedelta

import click
from flask import current_app
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import Customer, CustomerAccount, Job, JobPowder, Powder, User

__all__ = ["hello", "seed_data", "create_admin"]


@click.command("hello")
def hello() -> None:
    """Example CLI command."""
    current_app.logger.info("Hello from Chaotic Nexus!")


@click.command("seed-data")
@click.option("--force", is_flag=True, help="Truncate existing sample data before seeding.")
def seed_data(force: bool) -> None:
    """Populate the database with rich sample data for demos and local dev."""

    with current_app.app_context():
        if force:
            current_app.logger.info("Clearing existing sample data…")
            JobPowder.query.delete()
            Job.query.delete()
            CustomerAccount.query.delete()
            Customer.query.delete()
            Powder.query.delete()
            db.session.commit()

        if Customer.query.count() > 0:
            click.echo("Sample data already present. Use --force to reseed.")
            return

        now = datetime.utcnow()

        customers = [
            Customer(
                company="Acme Fabrication",
                contact_name="Alice Smith",
                phone="555-0100",
                email="alice@acmefab.ca",
                status="active",
                notes="Key enterprise account focused on architectural railings.",
            ),
            Customer(
                company="Island Builders Co.",
                contact_name="Bob Johnson",
                phone="555-0101",
                email="bob@islandbuilders.ca",
                status="active",
                notes="Prefers expedited turnaround on condo developments.",
            ),
            Customer(
                company="North Shore Marine",
                contact_name="Chloe Li",
                phone="555-0102",
                email="chloe@nsmarine.ca",
                status="prospect",
                notes="Marine coatings for ferry components.",
            ),
        ]
        db.session.add_all(customers)
        db.session.flush()

        powders = [
            Powder(
                powder_color="Tiger Drylac RAL 9005 Deep Black",
                manufacturer="Tiger Drylac",
                product_code="RAL9005",
                finish="Gloss",
                on_hand_kg=12.5,
                notes="House black kept in large stock.",
            ),
            Powder(
                powder_color="Prismatic Illusion Cherry",
                manufacturer="Prismatic Powders",
                product_code="PPB-4513",
                finish="Illusion",
                on_hand_kg=6.2,
                notes="Popular specialty color with premium pricing.",
            ),
            Powder(
                powder_color="Axalta Silver Vein",
                manufacturer="Axalta",
                product_code="SV-221",
                finish="Texture",
                on_hand_kg=9.0,
                notes="Used for commercial railing packages.",
            ),
        ]
        db.session.add_all(powders)
        db.session.flush()

        accounts = [
            CustomerAccount(
                email="customer@acmefab.ca",
                password_hash="hashed",
                first_name="Alice",
                last_name="Smith",
                customer=customers[0],
            ),
            CustomerAccount(
                email="projects@islandbuilders.ca",
                password_hash="hashed",
                first_name="Project",
                last_name="Team",
                customer=customers[1],
            ),
        ]
        db.session.add_all(accounts)
        db.session.flush()

        jobs = [
            Job(
                created_at=now - timedelta(days=6),
                date_in=now.date() - timedelta(days=6),
                due_by=now.date() + timedelta(days=3),
                company=customers[0].company,
                contact_name=customers[0].contact_name,
                status="in_work",
                priority="high",
                description="Fabricate and coat structural railing sections",
                customer=customers[0],
                customer_account=accounts[0],
                color=powders[0].powder_color,
            ),
            Job(
                created_at=now - timedelta(days=14),
                date_in=now.date() - timedelta(days=14),
                due_by=now.date() - timedelta(days=2),
                completed_at=now - timedelta(days=1),
                company=customers[0].company,
                contact_name=customers[0].contact_name,
                status="completed",
                description="Batch of metal patio furniture",
                customer=customers[0],
                customer_account=accounts[0],
                color=powders[1].powder_color,
            ),
            Job(
                created_at=now - timedelta(days=3),
                date_in=now.date() - timedelta(days=3),
                company=customers[1].company,
                contact_name=customers[1].contact_name,
                status="waiting_material",
                description="Balcony railing system for downtown condo",
                customer=customers[1],
                customer_account=accounts[1],
                color=powders[2].powder_color,
            ),
            Job(
                created_at=now - timedelta(days=1),
                date_in=now.date() - timedelta(days=1),
                company=customers[2].company,
                contact_name=customers[2].contact_name,
                status="intake",
                description="Marine winch housings requiring corrosion resistant finish",
                customer=customers[2],
                color=powders[0].powder_color,
            ),
        ]
        db.session.add_all(jobs)
        db.session.flush()

        job_powders = [
            JobPowder(job=jobs[0], powder=powders[0], quantity_used=3.5),
            JobPowder(job=jobs[1], powder=powders[1], quantity_used=4.1),
            JobPowder(job=jobs[2], powder=powders[2], quantity_used=2.7),
        ]
        db.session.add_all(job_powders)
        db.session.commit()

        click.echo("Seed data created: 3 customers, 2 portal accounts, 4 jobs, 3 powders.")


@click.command("create-admin")
@click.option("--username", required=True, help="Admin username")
@click.option("--password", required=True, help="Admin password")
def create_admin(username: str, password: str) -> None:
    """Create or update an admin user with the given credentials."""
    with current_app.app_context():
        user = User.query.filter_by(username=username).one_or_none()
        if user is None:
            user = User(username=username, is_admin=True)
            db.session.add(user)
        user.is_admin = True
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        click.echo(f"Admin user ensured: {username}")
