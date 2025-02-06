"""Agrega campos de colores QR a modelos relevantes

Revision ID: bfa6d2598f3b
Revises: d06faea1c24e
Create Date: 2025-02-06 15:14:05.149679

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bfa6d2598f3b'
down_revision = 'd06faea1c24e'
branch_labels = None
depends_on = None


def upgrade():
    # Para la tabla "bodegas": se asigna el server_default para que en los registros existentes se cargue el valor
    with op.batch_alter_table('bodegas', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'qr_fg_color', sa.String(length=7), nullable=False, server_default='#000000'))
        batch_op.add_column(sa.Column(
            'qr_bg_color', sa.String(length=7), nullable=False, server_default='#ffffff'))
    
    # Para la tabla "dashboard_items"
    with op.batch_alter_table('dashboard_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'qr_fg_color', sa.String(length=7), nullable=False, server_default='#000000'))
        batch_op.add_column(sa.Column(
            'qr_bg_color', sa.String(length=7), nullable=False, server_default='#ffffff'))
    
    # Para la tabla "pulzcards"
    with op.batch_alter_table('pulzcards', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'qr_fg_color', sa.String(length=7), nullable=False, server_default='#000000'))
        batch_op.add_column(sa.Column(
            'qr_bg_color', sa.String(length=7), nullable=False, server_default='#ffffff'))
    
    # Se actualizan algunos campos en "survey_responses" (esto se dejó como estaba generado)
    with op.batch_alter_table('survey_responses', schema=None) as batch_op:
        batch_op.alter_column('comment',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.Text(),
               existing_nullable=True)
        batch_op.alter_column('timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    
    # Para la tabla "tags"
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'qr_fg_color', sa.String(length=7), nullable=False, server_default='#000000'))
        batch_op.add_column(sa.Column(
            'qr_bg_color', sa.String(length=7), nullable=False, server_default='#ffffff'))


def downgrade():
    # En el downgrade se eliminan las columnas agregadas en el upgrade, en el orden inverso.
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.drop_column('qr_bg_color')
        batch_op.drop_column('qr_fg_color')
    
    with op.batch_alter_table('survey_responses', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
        batch_op.alter_column('comment',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=500),
               existing_nullable=True)
    
    with op.batch_alter_table('pulzcards', schema=None) as batch_op:
        batch_op.drop_column('qr_bg_color')
        batch_op.drop_column('qr_fg_color')
    
    with op.batch_alter_table('dashboard_items', schema=None) as batch_op:
        batch_op.drop_column('qr_bg_color')
        batch_op.drop_column('qr_fg_color')
    
    with op.batch_alter_table('bodegas', schema=None) as batch_op:
        batch_op.drop_column('qr_bg_color')
        batch_op.drop_column('qr_fg_color')