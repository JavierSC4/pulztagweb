"""Agregar columna must_change_password a la tabla user

Revision ID: b4d0c9525a51
Revises: b9e3b6031569
Create Date: 2024-11-13 11:50:50.936909

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4d0c9525a51'
down_revision = 'b9e3b6031569'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('must_change_password', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('must_change_password')

    # ### end Alembic commands ###
