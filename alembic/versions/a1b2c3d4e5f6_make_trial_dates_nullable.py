"""make trial subscription dates nullable

Revision ID: a1b2c3d4e5f6
Revises: 000000000001
Create Date: 2026-02-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '000000000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Таблица уже создана с nullable полями в initial migration
    # Эта миграция оставлена для совместимости
    pass


def downgrade() -> None:
    pass
