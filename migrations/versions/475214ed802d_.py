"""
1.14.0 Add short_code, program, domain to Study

Revision ID: 475214ed802d
Revises: 12850dab14e9
Create Date: 2021-06-09 00:28:30.170282
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '475214ed802d'
down_revision = '12850dab14e9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('study', sa.Column('short_code', sa.Text(), nullable=True))
    op.add_column('study', sa.Column('domain', sa.Text(), nullable=True))
    op.add_column('study', sa.Column('program', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('study', 'short_code')
    op.drop_column('study', 'program')
    op.drop_column('study', 'domain')
