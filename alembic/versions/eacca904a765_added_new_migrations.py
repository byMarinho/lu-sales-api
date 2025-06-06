"""Added new migrations

Revision ID: eacca904a765
Revises: 132f15b699ed
Create Date: 2025-05-25 18:21:13.411434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eacca904a765'
down_revision = '132f15b699ed'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Remover ENUM duplicado se existir
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('access_level', sa.Enum('admin', 'user', 'seller', name='accesslevel'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS accesslevel CASCADE;')
    # ### end Alembic commands ###