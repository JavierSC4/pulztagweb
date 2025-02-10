"""Pulzcards para guests

Revision ID: 1bf6552c2df1
Revises: 47dca2673f7c
Create Date: 2025-02-10 18:28:42.775382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bf6552c2df1'
down_revision = '47dca2673f7c'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Agregar la columna 'is_guest' como nullable con un valor por defecto en el servidor
    with op.batch_alter_table('pulzcards', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_guest', sa.Boolean(), nullable=True, server_default=sa.text('false'))
        )
        batch_op.add_column(
            sa.Column('expiration_date', sa.DateTime(), nullable=True)
        )
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)
    
    # 2. Actualizar los registros existentes: asignar false a 'is_guest'
    op.execute("UPDATE pulzcards SET is_guest = false WHERE is_guest IS NULL")
    
    # 3. Alterar la columna para que ya no permita valores nulos y quitar el server_default si lo deseas
    with op.batch_alter_table('pulzcards', schema=None) as batch_op:
        batch_op.alter_column(
            'is_guest',
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=None
        )


def downgrade():
    with op.batch_alter_table('pulzcards', schema=None) as batch_op:
        # Volver a hacer 'user_id' non-nullable
        batch_op.alter_column('user_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)
        batch_op.drop_column('expiration_date')
        batch_op.drop_column('is_guest')