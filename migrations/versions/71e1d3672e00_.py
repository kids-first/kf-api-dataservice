"""
1.9.0 Add study_code to Study

Revision ID: 71e1d3672e00
Revises: e37e013db6c7
Create Date: 2019-12-06 11:52:46.226608

"""
from alembic import op
import sqlalchemy as sa

from dataservice.api.common.model import KfId

# revision identifiers, used by Alembic.
revision = '71e1d3672e00'
down_revision = 'e37e013db6c7'
branch_labels = None
depends_on = None

# TODO - Populate with study code mappings for current studies
study_code_map = {}


def data_upgrades():
    """
    Populate Study.study_code column
    """
    connection = op.get_bind()

    study = sa.Table(
        'study',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11)),
        sa.Column('study_code', sa.String(), nullable=False, unique=True)
    )

    results = connection.execute(sa.select([
        study.c.kf_id,
        study.c.study_code
    ])).fetchall()

    for i, r in enumerate(results):
        kf_id = r[0]
        study_code = study_code_map.get(kf_id)
        if not study_code:
            raise Exception(
                f'Error in migration {revision}! Study {kf_id} has no '
                'study_code in map.'
            )
        connection.execute(
            study.update()
            .where(study.c.kf_id == kf_id)
            .values(study_code=study_code)
        )


def upgrade():
    op.add_column('study', sa.Column('study_code', sa.Text(), nullable=True))
    data_upgrades()
    op.alter_column('study', 'study_code', nullable=False)
    op.create_unique_constraint(None, 'study', ['study_code'])


def downgrade():
    op.drop_column('study', 'study_code')
