"""empty message

Revision ID: b209e801b850
Revises: 24fbdab8986b
Create Date: 2024-12-11 22:46:49.747514

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b209e801b850'
down_revision = '24fbdab8986b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop foreign key constraints and dependent tables in order
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('productos_caja_id_fkey', type_='foreignkey')

    # Drop 'cajas' table
    op.drop_table('cajas')

    # Drop 'bodegas' table
    op.drop_table('bodegas')

    # Recreate foreign key constraint for 'productos' pointing to the new table
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'caja', ['caja_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Recreate 'bodegas' table
    op.create_table('bodegas',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('id_bodega', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('nombre', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('ubicacion', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('notas', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('fecha_creacion', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('uuid', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='bodegas_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='bodegas_pkey'),
        sa.UniqueConstraint('id_bodega', name='bodegas_id_bodega_key'),
        sa.UniqueConstraint('uuid', name='bodegas_uuid_key')
    )

    # Recreate 'cajas' table
    op.create_table('cajas',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('id_caja', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
        sa.Column('nombre', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('categoria', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('notas', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('fecha_creacion', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('bodega_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('uuid', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['bodega_id'], ['bodegas.id'], name='cajas_bodega_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='cajas_pkey'),
        sa.UniqueConstraint('id_caja', name='cajas_id_caja_key'),
        sa.UniqueConstraint('uuid', name='cajas_uuid_key')
    )

    # Recreate foreign key constraint for 'productos'
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('productos_caja_id_fkey', 'cajas', ['caja_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###