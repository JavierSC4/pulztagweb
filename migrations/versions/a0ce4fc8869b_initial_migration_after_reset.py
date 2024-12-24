"""Initial migration after reset

Revision ID: a0ce4fc8869b
Revises: 
Create Date: 2024-12-24 16:16:27.348253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0ce4fc8869b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('dashboard_items', schema=None) as batch_op:
        batch_op.alter_column(
            'uuid',
            existing_type=sa.VARCHAR(length=36),
            type_=sa.UUID(),
            existing_nullable=False,
            postgresql_using='uuid::uuid'  # Especifica cómo convertir los datos
        )

def downgrade():
    with op.batch_alter_table('dashboard_items', schema=None) as batch_op:
        batch_op.alter_column(
            'uuid',
            existing_type=sa.UUID(),
            type_=sa.VARCHAR(length=36),
            existing_nullable=False,
            postgresql_using='uuid::varchar'  # Especifica cómo convertir los datos
        )
    # ### end Alembic commands ###
