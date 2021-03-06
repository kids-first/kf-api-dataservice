"""
1.0.1 - Add dbgap_consent_code to biospecimen

Revision ID: 8f1ad897fb0f
Revises: 7575993b35a7
Create Date: 2018-05-23 13:30:08.798811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f1ad897fb0f'
down_revision = '7575993b35a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('biospecimen', sa.Column(
        'dbgap_consent_code', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('biospecimen', 'dbgap_consent_code')
    # ### end Alembic commands ###
