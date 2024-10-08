"""
1.22.0 Add biobank_contact to Study table

Revision ID: 1f14248ec4cf
Revises: a67246728831
Create Date: 2024-06-06 13:38:44.771175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f14248ec4cf'
down_revision = 'a67246728831'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('study', sa.Column(
        'biobank_contact', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('study', 'biobank_contact')
    # ### end Alembic commands ###
