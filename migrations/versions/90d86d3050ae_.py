"""empty message

Revision ID: 90d86d3050ae
Revises: 7575993b35a7
Create Date: 2018-05-20 13:19:17.826653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90d86d3050ae'
down_revision = '7575993b35a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('biospecimen_participant_id_fkey', 'biospecimen', type_='foreignkey')
    op.create_foreign_key(None, 'biospecimen', 'participant', ['participant_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('cavatica_task_genomic_file_cavatica_task_id_fkey', 'cavatica_task_genomic_file', type_='foreignkey')
    op.drop_constraint('cavatica_task_genomic_file_genomic_file_id_fkey', 'cavatica_task_genomic_file', type_='foreignkey')
    op.create_foreign_key(None, 'cavatica_task_genomic_file', 'genomic_file', ['genomic_file_id'], ['kf_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'cavatica_task_genomic_file', 'cavatica_task', ['cavatica_task_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('diagnosis_participant_id_fkey', 'diagnosis', type_='foreignkey')
    op.create_foreign_key(None, 'diagnosis', 'participant', ['participant_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('family_relationship_participant_id_fkey', 'family_relationship', type_='foreignkey')
    op.drop_constraint('family_relationship_relative_id_fkey', 'family_relationship', type_='foreignkey')
    op.create_foreign_key(None, 'family_relationship', 'participant', ['relative_id'], ['kf_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'family_relationship', 'participant', ['participant_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('genomic_file_biospecimen_id_fkey', 'genomic_file', type_='foreignkey')
    op.drop_constraint('genomic_file_sequencing_experiment_id_fkey', 'genomic_file', type_='foreignkey')
    op.create_foreign_key(None, 'genomic_file', 'sequencing_experiment', ['sequencing_experiment_id'], ['kf_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'genomic_file', 'biospecimen', ['biospecimen_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('outcome_participant_id_fkey', 'outcome', type_='foreignkey')
    op.create_foreign_key(None, 'outcome', 'participant', ['participant_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('participant_study_id_fkey', 'participant', type_='foreignkey')
    op.create_foreign_key(None, 'participant', 'study', ['study_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('phenotype_participant_id_fkey', 'phenotype', type_='foreignkey')
    op.create_foreign_key(None, 'phenotype', 'participant', ['participant_id'], ['kf_id'], ondelete='CASCADE')
    op.drop_constraint('study_file_study_id_fkey', 'study_file', type_='foreignkey')
    op.create_foreign_key(None, 'study_file', 'study', ['study_id'], ['kf_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'study_file', type_='foreignkey')
    op.create_foreign_key('study_file_study_id_fkey', 'study_file', 'study', ['study_id'], ['kf_id'])
    op.drop_constraint(None, 'phenotype', type_='foreignkey')
    op.create_foreign_key('phenotype_participant_id_fkey', 'phenotype', 'participant', ['participant_id'], ['kf_id'])
    op.drop_constraint(None, 'participant', type_='foreignkey')
    op.create_foreign_key('participant_study_id_fkey', 'participant', 'study', ['study_id'], ['kf_id'])
    op.drop_constraint(None, 'outcome', type_='foreignkey')
    op.create_foreign_key('outcome_participant_id_fkey', 'outcome', 'participant', ['participant_id'], ['kf_id'])
    op.drop_constraint(None, 'genomic_file', type_='foreignkey')
    op.drop_constraint(None, 'genomic_file', type_='foreignkey')
    op.create_foreign_key('genomic_file_sequencing_experiment_id_fkey', 'genomic_file', 'sequencing_experiment', ['sequencing_experiment_id'], ['kf_id'])
    op.create_foreign_key('genomic_file_biospecimen_id_fkey', 'genomic_file', 'biospecimen', ['biospecimen_id'], ['kf_id'])
    op.drop_constraint(None, 'family_relationship', type_='foreignkey')
    op.drop_constraint(None, 'family_relationship', type_='foreignkey')
    op.create_foreign_key('family_relationship_relative_id_fkey', 'family_relationship', 'participant', ['relative_id'], ['kf_id'])
    op.create_foreign_key('family_relationship_participant_id_fkey', 'family_relationship', 'participant', ['participant_id'], ['kf_id'])
    op.drop_constraint(None, 'diagnosis', type_='foreignkey')
    op.create_foreign_key('diagnosis_participant_id_fkey', 'diagnosis', 'participant', ['participant_id'], ['kf_id'])
    op.drop_constraint(None, 'cavatica_task_genomic_file', type_='foreignkey')
    op.drop_constraint(None, 'cavatica_task_genomic_file', type_='foreignkey')
    op.create_foreign_key('cavatica_task_genomic_file_genomic_file_id_fkey', 'cavatica_task_genomic_file', 'genomic_file', ['genomic_file_id'], ['kf_id'])
    op.create_foreign_key('cavatica_task_genomic_file_cavatica_task_id_fkey', 'cavatica_task_genomic_file', 'cavatica_task', ['cavatica_task_id'], ['kf_id'])
    op.drop_constraint(None, 'biospecimen', type_='foreignkey')
    op.create_foreign_key('biospecimen_participant_id_fkey', 'biospecimen', 'participant', ['participant_id'], ['kf_id'])
    # ### end Alembic commands ###
