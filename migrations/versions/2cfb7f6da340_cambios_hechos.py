"""Cambios hechos

Revision ID: 2cfb7f6da340
Revises: a0ce4fc8869b
Create Date: 2024-12-24 18:44:32.733627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2cfb7f6da340'
down_revision = 'a0ce4fc8869b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('daily_views')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_views',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('views', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['dashboard_items.id'], name='daily_views_item_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='daily_views_pkey'),
    sa.UniqueConstraint('item_id', 'date', name='unique_item_date')
    )
    # ### end Alembic commands ###
