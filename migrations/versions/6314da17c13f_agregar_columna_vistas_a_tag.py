"""Agregar columna vistas a Tag

Revision ID: 6314da17c13f
Revises: b209e801b850
Create Date: 2024-12-13 12:35:34.512009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6314da17c13f'
down_revision = 'b209e801b850'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vistas', sa.Integer(), nullable=False, server_default='0'))
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.drop_column('vistas')
    # ### end Alembic commands ###

    # ### end Alembic commands ###
