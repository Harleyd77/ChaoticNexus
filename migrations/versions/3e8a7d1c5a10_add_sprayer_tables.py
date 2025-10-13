"""add sprayer tables

Revision ID: 3e8a7d1c5a10
Revises: 0a9a0b3a2c2b
Create Date: 2025-10-13 07:20:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3e8a7d1c5a10"
down_revision = "0a9a0b3a2c2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = set(inspector.get_table_names())

    if "spray_batch" not in tables:
        op.create_table(
            "spray_batch",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
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
            sa.Column("role", sa.String(length=50), nullable=True),
            sa.Column("operator", sa.Text(), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("start_weight_kg", sa.Numeric(10, 2), nullable=False),
            sa.Column("end_weight_kg", sa.Numeric(10, 2), nullable=True),
            sa.Column("used_kg", sa.Numeric(10, 2), nullable=True),
            sa.Column("duration_min", sa.Numeric(10, 2), nullable=True),
            sa.ForeignKeyConstraint(["powder_id"], ["powders.id"], ondelete="RESTRICT"),
        )

    if "spray_batch_jobs" not in tables:
        op.create_table(
            "spray_batch_jobs",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
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
            sa.Column("batch_id", sa.Integer(), nullable=False),
            sa.Column("job_id", sa.Integer(), nullable=False),
            sa.Column("time_min", sa.Numeric(10, 2), nullable=True),
            sa.Column("start_ts", sa.DateTime(timezone=True), nullable=True),
            sa.Column("end_ts", sa.DateTime(timezone=True), nullable=True),
            sa.Column("elapsed_seconds", sa.Numeric(12, 3), nullable=True),
            sa.Column("running_since", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["batch_id"], ["spray_batch.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        )


def downgrade() -> None:
    op.drop_table("spray_batch_jobs")
    op.drop_table("spray_batch")
