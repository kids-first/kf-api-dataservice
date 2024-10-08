"""
1.18.0 Add new columns to GenomicFile and SequencingExperiment to support Bix QC

Revision ID: 37449dd948c3
Revises: 1558052490ff
Create Date: 2024-03-26 09:39:14.971206
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37449dd948c3'
down_revision = '1558052490ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('genomic_file', sa.Column(
        'data_category', sa.Text(), nullable=True))
    op.add_column('genomic_file', sa.Column(
        'release_status', sa.Text(), nullable=True))
    op.add_column('genomic_file', sa.Column(
        'workflow_tool', sa.Text(), nullable=True))
    op.add_column('genomic_file', sa.Column(
        'workflow_type', sa.Text(), nullable=True))
    op.add_column('genomic_file', sa.Column(
        'workflow_version', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column(
        'adapter_sequencing', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column(
        'is_adapter_trimmed', sa.Boolean(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column(
        'read_pair_number', sa.Text(), nullable=True))
    op.add_column('sequencing_experiment', sa.Column(
        'target_capture_kit', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sequencing_experiment', 'target_capture_kit')
    op.drop_column('sequencing_experiment', 'read_pair_number')
    op.drop_column('sequencing_experiment', 'is_adapter_trimmed')
    op.drop_column('sequencing_experiment', 'adapter_sequencing')
    op.drop_column('genomic_file', 'workflow_version')
    op.drop_column('genomic_file', 'workflow_type')
    op.drop_column('genomic_file', 'workflow_tool')
    op.drop_column('genomic_file', 'release_status')
    op.drop_column('genomic_file', 'data_category')
    # ### end Alembic commands ###
