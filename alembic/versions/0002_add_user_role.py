"""add user role

Revision ID: 0002_add_user_role
Revises: 0001_init_tables
Create Date: 2026-05-19

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_add_user_role"
down_revision = "0001_init_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=20), server_default="user", nullable=True))


def downgrade() -> None:
    op.drop_column("users", "role")

