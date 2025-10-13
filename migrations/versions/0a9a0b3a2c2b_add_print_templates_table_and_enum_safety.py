"""add print_templates table and enum safety

Revision ID: 0a9a0b3a2c2b
Revises: e2e67964d977
Create Date: 2025-10-13 07:10:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0a9a0b3a2c2b"
down_revision = "e2e67964d977"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Create print_templates table if not exists (idempotent-ish)
    inspector = sa.inspect(conn)
    if "print_templates" not in inspector.get_table_names():
        # Drop pre-existing implicit sequence if a prior partial attempt created it
        op.execute("DROP SEQUENCE IF EXISTS print_templates_id_seq CASCADE")
        op.create_table(
            "print_templates",
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
            sa.Column("template_type", sa.String(length=120), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        )

    # Example enum safety: ensure 'QA' exists in jobs.status usage (string not enum in schema)
    # If using a real ENUM type later, add value here via ALTER TYPE ... ADD VALUE IF NOT EXISTS


def downgrade() -> None:
    # Safe to drop; table used only by app in this revision chain
    op.drop_table("print_templates")
