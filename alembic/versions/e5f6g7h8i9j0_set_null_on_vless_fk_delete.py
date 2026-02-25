"""set null on vless fk delete

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-02-26 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Изменяем FK в таблице subscribers
    op.drop_constraint('subscribers_vless_link_id_fkey', 'subscribers', type_='foreignkey')
    op.create_foreign_key(
        'subscribers_vless_link_id_fkey',
        'subscribers', 'vless_links',
        ['vless_link_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Изменяем FK в таблице trial_subscribers
    op.drop_constraint('trial_subscribers_vless_link_id_fkey', 'trial_subscribers', type_='foreignkey')
    op.create_foreign_key(
        'trial_subscribers_vless_link_id_fkey',
        'trial_subscribers', 'vless_links',
        ['vless_link_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Откатываем FK в таблице subscribers
    op.drop_constraint('subscribers_vless_link_id_fkey', 'subscribers', type_='foreignkey')
    op.create_foreign_key(
        'subscribers_vless_link_id_fkey',
        'subscribers', 'vless_links',
        ['vless_link_id'], ['id']
    )
    
    # Откатываем FK в таблице trial_subscribers
    op.drop_constraint('trial_subscribers_vless_link_id_fkey', 'trial_subscribers', type_='foreignkey')
    op.create_foreign_key(
        'trial_subscribers_vless_link_id_fkey',
        'trial_subscribers', 'vless_links',
        ['vless_link_id'], ['id']
    )
