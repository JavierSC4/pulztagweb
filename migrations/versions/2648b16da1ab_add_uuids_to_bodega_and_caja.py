from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '2648b16da1ab'
down_revision = None  # No hay migraciones anteriores
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columnas 'uuid' a las tablas 'bodega' y 'caja'
    op.add_column('bodega', sa.Column('uuid', sa.String(length=36), nullable=True))
    op.add_column('caja', sa.Column('uuid', sa.String(length=36), nullable=True))

    # Asignar UUIDs a registros existentes
    conn = op.get_bind()

    # Asignar UUIDs a 'bodega'
    bodega_result = conn.execute(sa.text("SELECT id FROM bodega"))
    for row in bodega_result:
        conn.execute(
            sa.text("UPDATE bodega SET uuid = :uuid WHERE id = :id"),
            {"uuid": str(uuid.uuid4()), "id": row.id}
        )

    # Asignar UUIDs a 'caja'
    caja_result = conn.execute(sa.text("SELECT id FROM caja"))
    for row in caja_result:
        conn.execute(
            sa.text("UPDATE caja SET uuid = :uuid WHERE id = :id"),
            {"uuid": str(uuid.uuid4()), "id": row.id}
        )

    # Hacer que las columnas 'uuid' sean NOT NULL y únicas
    op.alter_column('bodega', 'uuid', nullable=False)
    op.create_unique_constraint('uq_bodega_uuid', 'bodega', ['uuid'])

    op.alter_column('caja', 'uuid', nullable=False)
    op.create_unique_constraint('uq_caja_uuid', 'caja', ['uuid'])


def downgrade():
    # Revertir los cambios realizados en el upgrade
    op.drop_constraint('uq_caja_uuid', 'caja', type_='unique')
    op.alter_column('caja', 'uuid', nullable=True)
    op.drop_column('caja', 'uuid')

    op.drop_constraint('uq_bodega_uuid', 'bodega', type_='unique')
    op.alter_column('bodega', 'uuid', nullable=True)
    op.drop_column('bodega', 'uuid')