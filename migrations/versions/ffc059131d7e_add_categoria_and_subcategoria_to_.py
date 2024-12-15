"""Add categoria and subcategoria to Producto

Revision ID: ffc059131d7e
Revises: 2648b16da1ab
Create Date: 2024-12-11 15:08:26.683557
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ffc059131d7e'
down_revision = '2648b16da1ab'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columnas 'categoria' y 'subcategoria' a la tabla 'productos'
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('categoria', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('subcategoria', sa.String(length=100), nullable=True))


def downgrade():
    # Eliminar las columnas 'categoria' y 'subcategoria'
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_column('subcategoria')
        batch_op.drop_column('categoria')