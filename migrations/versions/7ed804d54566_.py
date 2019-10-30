"""
1.8.0 - Add new fields

- Add duo_ids to biospecimen
- Add library_prep, library_selection to sequencing_experiment
- Add species to participant

Revision ID: 7ed804d54566
Revises: 3affe0266c9d
Create Date: 2019-10-21 15:59:11.505995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7ed804d54566'
down_revision = '3affe0266c9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('biospecimen', sa.Column('duo_ids', postgresql.ARRAY(sa.Text()), nullable=True))
    op.add_column('participant', sa.Column('species', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column('library_prep', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column('library_selection', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sequencing_experiment', 'library_selection')
    op.drop_column('sequencing_experiment', 'library_prep')
    op.drop_column('participant', 'species')
    op.drop_column('biospecimen', 'duo_ids')
    # ### end Alembic commands ###
