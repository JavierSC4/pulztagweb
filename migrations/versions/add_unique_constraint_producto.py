from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'unique_producto_caja'
down_revision = 'ffc059131d7e'  # Asegúrate de que coincide con tu última migración
branch_labels = None
depends_on = None

def upgrade():
    # Agregar restricción única compuesta en (id_producto, caja_id)
    op.create_unique_constraint('uq_producto_caja', 'productos', ['id_producto', 'caja_id'])

def downgrade():
    # Eliminar la restricción única compuesta
    op.drop_constraint('uq_producto_caja', 'productos', type_='unique')