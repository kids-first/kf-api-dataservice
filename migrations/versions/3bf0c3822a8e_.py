"""
1.6.0 - Make sequencing_experiment and genomic_file many to many

Revision ID: 3bf0c3822a8e
Revises: 5f3a7baa3fda
Create Date: 2019-01-14 12:08:56.227298

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from dataservice.api.common.id_service import (
    uuid_generator,
    kf_id_generator
)
from dataservice.api.common.model import KfId

# revision identifiers, used by Alembic.
revision = '3bf0c3822a8e'
down_revision = '5f3a7baa3fda'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create sequencing_experiment_genomic_file association table
    Apply custom data modifications
    Drop sequencing_experiment columns
    """
    op.create_table('sequencing_experiment_genomic_file',
                    sa.Column('uuid', postgresql.UUID(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_at', sa.DateTime(), nullable=True),
                    sa.Column('visible', sa.Boolean(), server_default='true',
                              nullable=False),
                    sa.Column('sequencing_experiment_id',
                              KfId(length=11), nullable=False),
                    sa.Column('genomic_file_id', KfId(length=11),
                              nullable=False),
                    sa.Column('external_id', sa.Text(), nullable=True),
                    sa.Column('kf_id', KfId(length=11), nullable=False),
                    sa.ForeignKeyConstraint(['genomic_file_id'],
                                            ['genomic_file.kf_id'], ),
                    sa.ForeignKeyConstraint(['sequencing_experiment_id'], [
                                            'sequencing_experiment.kf_id'], ),
                    sa.PrimaryKeyConstraint('kf_id'),
                    sa.UniqueConstraint('sequencing_experiment_id',
                                        'genomic_file_id'),
                    sa.UniqueConstraint('uuid')
                    )

    data_upgrades()

    op.drop_constraint('genomic_file_sequencing_experiment_id_fkey',
                       'genomic_file', type_='foreignkey')
    op.drop_column('genomic_file', 'sequencing_experiment_id')


def data_upgrades():
    """
    COPY sequencing_experiment.genomic_file_id TO
    sequencing_experiment_genomic_file.sequencing_experiment_id
    COPY sequencing_experiment.kf_id TO
    sequencing_experiment_genomic_file.sequencing_experiment_id
    """
    connection = op.get_bind()

    sequencing_experiment_genomic_file = sa.Table(
        'sequencing_experiment_genomic_file',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11), default=kf_id_generator('RF')),
        sa.Column('genomic_file_id', KfId(length=11)),
        sa.Column('sequencing_experiment_id', KfId(length=11)),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('modified_at', sa.DateTime(), default=datetime.now),
        sa.Column('uuid', postgresql.UUID(), nullable=True,
                  default=uuid_generator)
    )

    genomic_file = sa.Table(
        'genomic_file',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11)),
        sa.Column('sequencing_experiment_id', KfId(length=11))
    )

    results = connection.execute(sa.select([
        genomic_file.c.kf_id,
        genomic_file.c.sequencing_experiment_id
    ])).fetchall()

    for gf, seq_exp in results:
        if not gf or not seq_exp:
            continue
        connection.execute(sequencing_experiment_genomic_file.insert().values(
            genomic_file_id=gf,
            sequencing_experiment_id=seq_exp))


def data_downgrades():
    """
    COPY sequencing_experiment_genomic_file.genomic_file_id TO
    sequencing_experiment.genomic_file_id
    # NB This will lose all information relating many files to
    one sequencing_experiment
    """

    connection = op.get_bind()

    sequencing_experiment_genomic_file = sa.Table(
        'sequencing_experiment_genomic_file',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11), default=kf_id_generator('RF')),
        sa.Column('genomic_file_id', KfId(length=11)),
        sa.Column('sequencing_experiment_id', KfId(length=11)),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('modified_at', sa.DateTime(), default=datetime.now),
        sa.Column('uuid', postgresql.UUID(), nullable=True,
                  default=uuid_generator)
    )

    genomic_file = sa.Table(
        'genomic_file',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11)),
        sa.Column('sequencing_experiment_id', KfId(length=11))
    )

    results = connection.execute(sa.select([
        sequencing_experiment_genomic_file.c.genomic_file_id,
        sequencing_experiment_genomic_file.c.sequencing_experiment_id,
    ])).fetchall()

    for gf, seq_exp in results:
        if not gf or not seq_exp:
            continue
        connection.execute(
            genomic_file.update().where(
                genomic_file.c.kf_id == gf)
            .values(sequencing_experiment_id=seq_exp)
        )


def downgrade():
    """
    Reverse changes from upgrade()
    """
    op.add_column('genomic_file', sa.Column('sequencing_experiment_id',
                                            sa.VARCHAR(length=11),
                                            autoincrement=False,
                                            nullable=True))
    op.create_foreign_key('genomic_file_sequencing_experiment_id_fkey',
                          'genomic_file',
                          'sequencing_experiment',
                          ['sequencing_experiment_id'], ['kf_id'])

    data_downgrades()

    op.drop_table('sequencing_experiment_genomic_file')
