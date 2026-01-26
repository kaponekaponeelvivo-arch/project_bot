"""create notification_limits

Revision ID: 4549a2592479
Revises: a4ef69f8d578
Create Date: 2026-01-26 22:38:37.333618
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4549a2592479"
down_revision: Union[str, Sequence[str], None] = "a4ef69f8d578"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create notification_limits table."""
    op.create_table(
        "notification_limits",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("sent_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("telegram_id", "date"),
    )


def downgrade() -> None:
    """Drop notification_limits table."""
    op.drop_table("notification_limits")
