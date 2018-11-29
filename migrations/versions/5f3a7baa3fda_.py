"""
1.5.0 - Rename cavatica_task to task, rename cavatica_task_genomic_file to task_genomic_file

Revision ID: 5f3a7baa3fda
Revises: dd4c7a3ec1be
Create Date: 2018-11-12 12:48:17.005235

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5f3a7baa3fda'
down_revision = 'dd4c7a3ec1be'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('cavatica_task', 'task')
    op.alter_column('task', 'external_cavatica_task_id',
                    new_column_name='external_task_id')

    op.rename_table('cavatica_task_genomic_file', 'task_genomic_file')
    op.alter_column('task_genomic_file', 'cavatica_task_id',
                    new_column_name='task_id')


def downgrade():
    op.rename_table('task', 'cavatica_task')
    op.alter_column('cavatica_task', 'external_task_id',
                    new_column_name='external_cavatica_task_id')

    op.rename_table('task_genomic_file', 'cavatica_task_genomic_file')
    op.alter_column('cavatica_task_genomic_file', 'task_id',
                    new_column_name='cavatica_task_id')
