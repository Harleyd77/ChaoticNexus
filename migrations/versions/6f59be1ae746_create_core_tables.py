"""create core tables

Revision ID: 6f59be1ae746
Revises:
Create Date: 2025-10-12 11:19:40.428305

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6f59be1ae746"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("email_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reset_token", sa.String(length=255), nullable=True),
        sa.Column("reset_token_expires", sa.DateTime(timezone=True), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customer_accounts_email", "customer_accounts", ["email"], unique=True)

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("phone_ext", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("street", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=30), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("tax_id", sa.String(length=120), nullable=True),
        sa.Column("account_number", sa.String(length=120), nullable=True),
        sa.Column("terms", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_company", "customers", ["company"], unique=True)

    op.create_foreign_key(
        "fk_customer_accounts_customer_id",
        "customer_accounts",
        "customers",
        ["customer_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "powders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("powder_color", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("product_code", sa.String(length=120), nullable=True),
        sa.Column("gloss_level", sa.String(length=120), nullable=True),
        sa.Column("finish", sa.String(length=120), nullable=True),
        sa.Column("metallic", sa.Integer(), nullable=True),
        sa.Column("needs_clear", sa.Integer(), nullable=True),
        sa.Column("int_ext", sa.String(length=120), nullable=True),
        sa.Column("additional_code", sa.String(length=120), nullable=True),
        sa.Column("msds_url", sa.Text(), nullable=True),
        sa.Column("sds_url", sa.Text(), nullable=True),
        sa.Column("web_link", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("additional_info", sa.Text(), nullable=True),
        sa.Column("cure_schedule", sa.Text(), nullable=True),
        sa.Column("price_per_kg", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("charge_per_lb", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("weight_box_kg", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("last_price_check", sa.DateTime(timezone=True), nullable=True),
        sa.Column("in_stock", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("shipping_cost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("picture_url", sa.Text(), nullable=True),
        sa.Column("color_family", sa.String(length=120), nullable=True),
        sa.Column("aliases", sa.Text(), nullable=True),
        sa.Column("on_hand_kg", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("last_weighed_kg", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("last_weighed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_powders_powder_color", "powders", ["powder_color"], unique=False)

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("permissions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("ext", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_in", sa.Date(), nullable=True),
        sa.Column("due_by", sa.Date(), nullable=True),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("po", sa.String(length=120), nullable=True),
        sa.Column("type", sa.String(length=120), nullable=True),
        sa.Column("intake_source", sa.String(length=120), nullable=True),
        sa.Column("priority", sa.String(length=60), nullable=True),
        sa.Column("blast", sa.String(length=120), nullable=True),
        sa.Column("prep", sa.String(length=120), nullable=True),
        sa.Column("color", sa.String(length=120), nullable=True),
        sa.Column("color_source", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("department", sa.String(length=60), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("work_order_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("archived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("archived_reason", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=True),
        sa.Column("on_screen", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("screen_order_index", sa.Integer(), nullable=True),
        sa.Column(
            "submitted_by_customer", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "requires_approval", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("customer_notes", sa.Text(), nullable=True),
        sa.Column("shop_notes", sa.Text(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("customer_account_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["customer_account_id"],
            ["customer_accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_company", "jobs", ["company"], unique=False)
    op.create_index("ix_jobs_status", "jobs", ["status"], unique=False)

    op.create_table(
        "inventory_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("powder_id", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=120), nullable=False),
        sa.Column("old_value", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("new_value", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["powder_id"], ["powders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reorder_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("powder_id", sa.Integer(), nullable=True),
        sa.Column("low_stock_threshold", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("reorder_quantity", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("supplier_info", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["powder_id"], ["powders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "job_edit_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("field_name", sa.String(length=120), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column(
            "changed_by_customer", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customer_accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_edit_history_job_id", "job_edit_history", ["job_id"], unique=False)

    op.create_table(
        "job_photos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_photos_job_id", "job_photos", ["job_id"], unique=False)

    op.create_table(
        "job_powders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("powder_id", sa.Integer(), nullable=True),
        sa.Column("powder_color", sa.String(length=255), nullable=True),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("quantity_used", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["powder_id"], ["powders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "powder_usage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("powder_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("amount_used", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["powder_id"], ["powders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "time_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("start_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("minutes", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_time_logs_job_id", "time_logs", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_constraint("fk_customer_accounts_customer_id", "customer_accounts", type_="foreignkey")
    op.drop_index("ix_time_logs_job_id", table_name="time_logs")
    op.drop_table("time_logs")
    op.drop_table("powder_usage")
    op.drop_table("job_powders")
    op.drop_index("ix_job_photos_job_id", table_name="job_photos")
    op.drop_table("job_photos")
    op.drop_index("ix_job_edit_history_job_id", table_name="job_edit_history")
    op.drop_table("job_edit_history")
    op.drop_table("reorder_settings")
    op.drop_table("inventory_log")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_company", table_name="jobs")
    op.drop_table("jobs")
    op.drop_table("contacts")
    op.drop_table("users")
    op.drop_table("settings")
    op.drop_index("ix_powders_powder_color", table_name="powders")
    op.drop_table("powders")
    op.drop_index("ix_customers_company", table_name="customers")
    op.drop_table("customers")
    op.drop_index("ix_customer_accounts_email", table_name="customer_accounts")
    op.drop_table("customer_accounts")
