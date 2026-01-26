"""physically create subscriptions table

Revision ID: cc5081ed320d
Revises: d87602049252
Create Date: 2026-01-26 09:21:44.886451
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cc5081ed320d"
down_revision: Union[str, Sequence[str], None] = "d87602049252"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("plan", sa.String(length=50), nullable=False),
        sa.Column("days", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("subscriptions")
