"""
Add columns to study_file

Revision ID: 83788dfcbd00
Revises: 243980a97e4c
Create Date: 2018-04-24 09:20:50.988890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '83788dfcbd00'
down_revision = '4a7f7cb8ac00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('study_file', sa.Column('data_type', sa.Text(), nullable=True))
    op.add_column('study_file', sa.Column('file_format', sa.Text(), nullable=True))
    op.add_column('study_file', sa.Column('latest_did', postgresql.UUID(), nullable=False))
    op.drop_column('study_file', 'file_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('study_file', sa.Column('file_name', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('study_file', 'latest_did')
    op.drop_column('study_file', 'file_format')
    op.drop_column('study_file', 'data_type')
    # ### end Alembic commands ###
