"""
1.1.2 - Rename family_relationship columns

Manually rename columns using ALTER TABLE
Don't use alembic's autogenerated migration since it generates
code to drop the existing columns and create new ones

Revision ID: ce359a457d3d
Revises: 5b903b00dce4
Create Date: 2018-06-20 15:00:55.238774

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ce359a457d3d'
down_revision = '5b903b00dce4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('family_relationship', 'participant_id',
                    new_column_name='participant1_id')
    op.alter_column('family_relationship', 'relative_id',
                    new_column_name='participant2_id')
    op.alter_column('family_relationship', 'participant_to_relative_relation',
                    new_column_name='participant1_to_participant2_relation')
    op.alter_column('family_relationship', 'relative_to_participant_relation',
                    new_column_name='participant2_to_participant1_relation')


def downgrade():
    op.alter_column('family_relationship', 'participant1_id',
                    new_column_name='participant_id')
    op.alter_column('family_relationship', 'participant2_id',
                    new_column_name='relative_id')
    op.alter_column('family_relationship',
                    'participant1_to_participant2_relation',
                    new_column_name='participant_to_relative_relation')
    op.alter_column('family_relationship',
                    'participant2_to_participant1_relation',
                    new_column_name='relative_to_participant_relation')