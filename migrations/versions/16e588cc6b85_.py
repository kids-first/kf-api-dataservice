"""
Add visibility_reason and visibility_comment columns to capture
justification for visibility value

Revision ID: 16e588cc6b85
Revises: 475214ed802d
Create Date: 2023-03-16 13:15:59.929140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16e588cc6b85'
down_revision = '475214ed802d'
branch_labels = None
depends_on = None


def add_visibility_reason():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alias_group', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('biospecimen', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('biospecimen_diagnosis', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    op.add_column('biospecimen_genomic_file', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    op.add_column('cavatica_app', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('diagnosis', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('family', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('family_relationship', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    op.add_column('genomic_file', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('investigator', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('outcome', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('participant', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('phenotype', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('read_group', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('read_group_genomic_file', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    op.add_column('sequencing_center', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment_genomic_file', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    op.add_column('study', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('study_file', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('task', sa.Column('visibility_reason',
                  sa.Text(), nullable=True))
    op.add_column('task_genomic_file', sa.Column(
        'visibility_reason', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def remove_visibility_reason():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task_genomic_file', 'visibility_reason')
    op.drop_column('task', 'visibility_reason')
    op.drop_column('study_file', 'visibility_reason')
    op.drop_column('study', 'visibility_reason')
    op.drop_column('sequencing_experiment_genomic_file', 'visibility_reason')
    op.drop_column('sequencing_experiment', 'visibility_reason')
    op.drop_column('sequencing_center', 'visibility_reason')
    op.drop_column('read_group_genomic_file', 'visibility_reason')
    op.drop_column('read_group', 'visibility_reason')
    op.drop_column('phenotype', 'visibility_reason')
    op.drop_column('participant', 'visibility_reason')
    op.drop_column('outcome', 'visibility_reason')
    op.drop_column('investigator', 'visibility_reason')
    op.drop_column('genomic_file', 'visibility_reason')
    op.drop_column('family_relationship', 'visibility_reason')
    op.drop_column('family', 'visibility_reason')
    op.drop_column('diagnosis', 'visibility_reason')
    op.drop_column('cavatica_app', 'visibility_reason')
    op.drop_column('biospecimen_genomic_file', 'visibility_reason')
    op.drop_column('biospecimen_diagnosis', 'visibility_reason')
    op.drop_column('biospecimen', 'visibility_reason')
    op.drop_column('alias_group', 'visibility_reason')
    # ### end Alembic commands ###

def add_visibility_comment():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alias_group', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('biospecimen', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('biospecimen_diagnosis', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('biospecimen_genomic_file', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('cavatica_app', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('diagnosis', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('family', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('family_relationship', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('genomic_file', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('investigator', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('outcome', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('participant', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('phenotype', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('read_group', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('read_group_genomic_file', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('sequencing_center', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment_genomic_file', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('study', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('study_file', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('task', sa.Column('visibility_comment', sa.Text(), nullable=True))
    op.add_column('task_genomic_file', sa.Column('visibility_comment', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def remove_visibility_comment():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task_genomic_file', 'visibility_comment')
    op.drop_column('task', 'visibility_comment')
    op.drop_column('study_file', 'visibility_comment')
    op.drop_column('study', 'visibility_comment')
    op.drop_column('sequencing_experiment_genomic_file', 'visibility_comment')
    op.drop_column('sequencing_experiment', 'visibility_comment')
    op.drop_column('sequencing_center', 'visibility_comment')
    op.drop_column('read_group_genomic_file', 'visibility_comment')
    op.drop_column('read_group', 'visibility_comment')
    op.drop_column('phenotype', 'visibility_comment')
    op.drop_column('participant', 'visibility_comment')
    op.drop_column('outcome', 'visibility_comment')
    op.drop_column('investigator', 'visibility_comment')
    op.drop_column('genomic_file', 'visibility_comment')
    op.drop_column('family_relationship', 'visibility_comment')
    op.drop_column('family', 'visibility_comment')
    op.drop_column('diagnosis', 'visibility_comment')
    op.drop_column('cavatica_app', 'visibility_comment')
    op.drop_column('biospecimen_genomic_file', 'visibility_comment')
    op.drop_column('biospecimen_diagnosis', 'visibility_comment')
    op.drop_column('biospecimen', 'visibility_comment')
    op.drop_column('alias_group', 'visibility_comment')
    # ### end Alembic commands ###

def upgrade():
    add_visibility_reason()
    add_visibility_comment()

def downgrade():
    remove_visibility_reason()
    remove_visibility_comment()
