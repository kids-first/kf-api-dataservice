"""
Add family relationship table

Revision ID: c60110f2a43a
Revises: 9ff025c8ba49
Create Date: 2018-02-19 09:55:37.440875

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c60110f2a43a'
down_revision = '9ff025c8ba49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family_relationship',
    sa.Column('uuid', postgresql.UUID(), nullable=True),
    sa.Column('kf_id', sa.String(length=8), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('participant_id', sa.String(length=8), nullable=False),
    sa.Column('relative_id', sa.String(length=8), nullable=False),
    sa.Column('participant_to_relative_relation', sa.Text(), nullable=False),
    sa.Column('relative_to_participant_relation', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['participant_id'], ['participant.kf_id'], ),
    sa.ForeignKeyConstraint(['relative_id'], ['participant.kf_id'], ),
    sa.PrimaryKeyConstraint('kf_id'),
    sa.UniqueConstraint('kf_id'),
    sa.UniqueConstraint('participant_id', 'relative_id', 'participant_to_relative_relation', 'relative_to_participant_relation'),
    sa.UniqueConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('family_relationship')
    # ### end Alembic commands ###