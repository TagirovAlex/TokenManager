"""add attribute_defs and attr_values

Revision ID: add_attrs
Revises: 
Create Date: 2026-04-22 13:06:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'add_attrs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('attribute_defs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('category_id', sa.String(36), sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('field_type', sa.String(20), nullable=False),
        sa.Column('min_value', sa.Integer(), nullable=True),
        sa.Column('max_value', sa.Integer(), nullable=True),
        sa.Column('step', sa.Integer(), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('is_required', sa.Boolean(), default=False),
    )
    
    op.create_table('attr_values',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('object_id', sa.String(36), sa.ForeignKey('objects.id'), nullable=False),
        sa.Column('attribute_def_id', sa.String(36), sa.ForeignKey('attribute_defs.id'), nullable=False),
        sa.Column('bool_value', sa.Boolean(), nullable=True),
        sa.Column('int_value', sa.Integer(), nullable=True),
        sa.Column('str_value', sa.String(500), nullable=True),
    )


def downgrade():
    op.drop_table('attr_values')
    op.drop_table('attribute_defs')