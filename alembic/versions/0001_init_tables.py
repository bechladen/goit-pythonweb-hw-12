"""init tables

Revision ID: 0001_init_tables
Revises: 
Create Date: 2026-05-19

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("avatar", sa.String(length=255), nullable=True),
        sa.Column("confirmed", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=False),
        sa.Column("extra", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("email", "user_id", name="uq_contacts_email_user"),
    )
    op.create_index("ix_contacts_email", "contacts", ["email"])
    op.create_index("ix_contacts_user_id", "contacts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_contacts_user_id", table_name="contacts")
    op.drop_index("ix_contacts_email", table_name="contacts")
    op.drop_table("contacts")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
