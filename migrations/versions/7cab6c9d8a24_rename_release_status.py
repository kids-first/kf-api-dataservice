"""
1.19.0 Rename release_status to file_version_descriptor

Revision ID: 7cab6c9d8a24
Revises: 1dd6c503d77f
Create Date: 2024-04-15 16:07:44.081102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cab6c9d8a24'
down_revision = '1dd6c503d77f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('genomic_file', sa.Column('file_version_descriptor', sa.Text(), nullable=True))
    op.drop_column('genomic_file', 'release_status')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('genomic_file', sa.Column('release_status', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('genomic_file', 'file_version_descriptor')
    # ### end Alembic commands ###