"""initial tables

Revision ID: 000000000001
Revises: 
Create Date: 2026-02-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000000000001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу images
    op.create_table('images',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('image', sa.LargeBinary(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу users
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('user_name', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('admin_status', sa.String(), nullable=False, server_default='user'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Создаем таблицу vless_links
    op.create_table('vless_links',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('src', sa.String(), nullable=False),
        sa.Column('add_att', sa.DateTime(), nullable=False),
        sa.Column('using', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу subscribers
    op.create_table('subscribers',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='not active'),
        sa.Column('vless_link_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['vless_link_id'], ['vless_links.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Создаем таблицу trial_subscribers
    op.create_table('trial_subscribers',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('trial_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('vless_link_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['vless_link_id'], ['vless_links.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Создаем таблицу payment_history
    op.create_table('payment_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('date_paid', sa.DateTime(), nullable=False),
        sa.Column('payment_amount', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('payment_history')
    op.drop_table('trial_subscribers')
    op.drop_table('subscribers')
    op.drop_table('vless_links')
    op.drop_table('users')
    op.drop_table('images')
