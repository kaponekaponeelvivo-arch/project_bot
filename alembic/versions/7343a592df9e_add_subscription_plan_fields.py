"""add subscription plan fields

Revision ID: 7343a592df9e
Revises: f5a2e8806d39
Create Date: 2026-01-26

This is a FIXATION migration.
Columns already exist in the database.
No schema changes are performed.
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "7343a592df9e"
down_revision: Union[str, Sequence[str], None] = "f5a2e8806d39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Columns already exist in database.
    This migration only marks schema as up-to-date.
    """
    pass


def downgrade() -> None:
    """
    Downgrade is intentionally disabled.
    """
    pass
