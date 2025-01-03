"""Añadidos comentarios a la encuesta

Revision ID: ab3b1ceffcc6
Revises: 
Create Date: 2024-12-25 14:03:49.421312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab3b1ceffcc6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('survey_responses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('survey_responses', schema=None) as batch_op:
        batch_op.drop_column('comment')

    # ### end Alembic commands ###
