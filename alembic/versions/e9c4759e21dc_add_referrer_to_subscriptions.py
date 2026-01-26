"""add referrer to subscriptions

Revision ID: e9c4759e21dc
Revises: cc5081ed320d
Create Date: 2026-01-26 09:34:21.020620
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e9c4759e21dc"
down_revision: Union[str, Sequence[str], None] = "cc5081ed320d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column("referrer_telegram_id", sa.BigInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "referrer_telegram_id")
