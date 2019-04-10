"""
1.7.0 - Add indices to created_at columns

Revision ID: 3affe0266c9d
Revises: bac1c51fa94c
Create Date: 2019-04-10 09:48:26.159346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3affe0266c9d'
down_revision = 'bac1c51fa94c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_alias_group_created_at'), 'alias_group', ['created_at'], unique=False)
    op.create_index(op.f('ix_biospecimen_created_at'), 'biospecimen', ['created_at'], unique=False)
    op.create_index(op.f('ix_biospecimen_diagnosis_created_at'), 'biospecimen_diagnosis', ['created_at'], unique=False)
    op.create_index(op.f('ix_biospecimen_genomic_file_created_at'), 'biospecimen_genomic_file', ['created_at'], unique=False)
    op.create_index(op.f('ix_cavatica_app_created_at'), 'cavatica_app', ['created_at'], unique=False)
    op.create_index(op.f('ix_diagnosis_created_at'), 'diagnosis', ['created_at'], unique=False)
    op.create_index(op.f('ix_family_created_at'), 'family', ['created_at'], unique=False)
    op.create_index(op.f('ix_family_relationship_created_at'), 'family_relationship', ['created_at'], unique=False)
    op.create_index(op.f('ix_genomic_file_created_at'), 'genomic_file', ['created_at'], unique=False)
    op.create_index(op.f('ix_investigator_created_at'), 'investigator', ['created_at'], unique=False)
    op.create_index(op.f('ix_outcome_created_at'), 'outcome', ['created_at'], unique=False)
    op.create_index(op.f('ix_participant_created_at'), 'participant', ['created_at'], unique=False)
    op.create_index(op.f('ix_phenotype_created_at'), 'phenotype', ['created_at'], unique=False)
    op.create_index(op.f('ix_read_group_created_at'), 'read_group', ['created_at'], unique=False)
    op.create_index(op.f('ix_read_group_genomic_file_created_at'), 'read_group_genomic_file', ['created_at'], unique=False)
    op.create_index(op.f('ix_sequencing_center_created_at'), 'sequencing_center', ['created_at'], unique=False)
    op.create_index(op.f('ix_sequencing_experiment_created_at'), 'sequencing_experiment', ['created_at'], unique=False)
    op.create_index(op.f('ix_sequencing_experiment_genomic_file_created_at'), 'sequencing_experiment_genomic_file', ['created_at'], unique=False)
    op.create_index(op.f('ix_study_created_at'), 'study', ['created_at'], unique=False)
    op.create_index(op.f('ix_study_file_created_at'), 'study_file', ['created_at'], unique=False)
    op.create_index(op.f('ix_task_created_at'), 'task', ['created_at'], unique=False)
    op.create_index(op.f('ix_task_genomic_file_created_at'), 'task_genomic_file', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_task_genomic_file_created_at'), table_name='task_genomic_file')
    op.drop_index(op.f('ix_task_created_at'), table_name='task')
    op.drop_index(op.f('ix_study_file_created_at'), table_name='study_file')
    op.drop_index(op.f('ix_study_created_at'), table_name='study')
    op.drop_index(op.f('ix_sequencing_experiment_genomic_file_created_at'), table_name='sequencing_experiment_genomic_file')
    op.drop_index(op.f('ix_sequencing_experiment_created_at'), table_name='sequencing_experiment')
    op.drop_index(op.f('ix_sequencing_center_created_at'), table_name='sequencing_center')
    op.drop_index(op.f('ix_read_group_genomic_file_created_at'), table_name='read_group_genomic_file')
    op.drop_index(op.f('ix_read_group_created_at'), table_name='read_group')
    op.drop_index(op.f('ix_phenotype_created_at'), table_name='phenotype')
    op.drop_index(op.f('ix_participant_created_at'), table_name='participant')
    op.drop_index(op.f('ix_outcome_created_at'), table_name='outcome')
    op.drop_index(op.f('ix_investigator_created_at'), table_name='investigator')
    op.drop_index(op.f('ix_genomic_file_created_at'), table_name='genomic_file')
    op.drop_index(op.f('ix_family_relationship_created_at'), table_name='family_relationship')
    op.drop_index(op.f('ix_family_created_at'), table_name='family')
    op.drop_index(op.f('ix_diagnosis_created_at'), table_name='diagnosis')
    op.drop_index(op.f('ix_cavatica_app_created_at'), table_name='cavatica_app')
    op.drop_index(op.f('ix_biospecimen_genomic_file_created_at'), table_name='biospecimen_genomic_file')
    op.drop_index(op.f('ix_biospecimen_diagnosis_created_at'), table_name='biospecimen_diagnosis')
    op.drop_index(op.f('ix_biospecimen_created_at'), table_name='biospecimen')
    op.drop_index(op.f('ix_alias_group_created_at'), table_name='alias_group')
    # ### end Alembic commands ###
