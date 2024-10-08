"""
1.26.0 add vbr fields

Revision ID: 9f5a6dbfec37
Revises: 869f891d97ad
Create Date: 2024-09-05 16:47:44.222329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f5a6dbfec37'
down_revision = '869f891d97ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('biospecimen', sa.Column('has_matched_normal_sample', sa.Boolean(), nullable=True))
    op.add_column('sample', sa.Column('external_collection_id', sa.Text(), nullable=True))
    op.add_column('sample', sa.Column('has_matched_normal_sample', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sample', 'has_matched_normal_sample')
    op.drop_column('sample', 'external_collection_id')
    op.drop_column('biospecimen', 'has_matched_normal_sample')
    # ### end Alembic commands ###
