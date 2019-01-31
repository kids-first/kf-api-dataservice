"""
1.6.1 - Fix KF ID prefix on sequencing_experiment_genomic_file records

Prefix 'RF' was used rather than the correct one, 'SG'

Revision ID: bac1c51fa94c
Revises: 3bf0c3822a8e
Create Date: 2019-01-31 10:10:04.296502
"""
from alembic import op
import sqlalchemy as sa

from dataservice.api.common.model import KfId

# revision identifiers, used by Alembic.
revision = 'bac1c51fa94c'
down_revision = '3bf0c3822a8e'
branch_labels = None
depends_on = None


def upgrade():
    """
    Replace prefix of every KF ID in sequencing_experiment_genomic_file
    with the correct prefix
    """
    _update_ids('SG')


def downgrade():
    """
    Undo what upgrade does
    """
    _update_ids('RF')


def _update_ids(table_prefix):
    """
    Update all KF IDs of sequencing_experiment_genomic_file records by
    replacing the current KF ID's 2 char prefix with a new 2 char prefix

    :param table_prefix: the new KF ID prefix
    :type table_prefix: str
    """
    connection = op.get_bind()

    sequencing_experiment_genomic_file = sa.Table(
        'sequencing_experiment_genomic_file',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11))
    )

    results = connection.execute(sa.select(
        [sequencing_experiment_genomic_file.c.kf_id]
    )).fetchall()

    for r in results:
        kf_id = r[0]
        # Skip any that are already correct
        if kf_id.startswith(table_prefix):
            continue

        delimiter = '_'
        suffix = kf_id.split(delimiter)[-1]
        new_kf_id = delimiter.join([table_prefix, suffix])

        connection.execute(
            sequencing_experiment_genomic_file.update()
            .where(sequencing_experiment_genomic_file.c.kf_id == kf_id)
            .values(kf_id=new_kf_id)
        )
