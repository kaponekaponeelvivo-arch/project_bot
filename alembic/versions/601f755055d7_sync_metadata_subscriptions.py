"""sync metadata: subscriptions

Revision ID: 601f755055d7
Revises: b348d0e110dd
Create Date: 2026-01-26 20:54:53.778769
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "601f755055d7"
down_revision: Union[str, Sequence[str], None] = "b348d0e110dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema (squashed state)."""
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")
    op.create_index(
        op.f("ix_subscriptions_telegram_id"),
        "subscriptions",
        ["telegram_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema (legacy rollback)."""
    op.drop_index(op.f("ix_subscriptions_telegram_id"), table_name="subscriptions")

    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BIGINT(), nullable=False),
        sa.Column("username", sa.VARCHAR(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(), nullable=False),
        sa.Column("is_active", sa.BOOLEAN(), nullable=False),
        sa.Column("subscription_until", postgresql.TIMESTAMP(), nullable=True),
        sa.Column("referred_by", sa.BIGINT(), nullable=True),
        sa.Column("referrals_count", sa.INTEGER(), nullable=False),
        sa.Column("subscription_plan", sa.VARCHAR(), nullable=True),
        sa.Column("subscription_days_total", sa.INTEGER(), nullable=False),
        sa.PrimaryKeyConstraint("telegram_id", name=op.f("users_pkey")),
    )

    op.create_index(
        op.f("ix_users_telegram_id"),
        "users",
        ["telegram_id"],
        unique=False,
    )
