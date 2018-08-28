"""
1.4.0 - Make read_group genomic_file many to many

Revision ID: c89fea71ca43
Revises: cdbd609e2bd5
Create Date: 2018-08-27 10:12:18.690594

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from dataservice.api.common.id_service import uuid_generator, kf_id_generator
from dataservice.api.common.model import KfId

# revision identifiers, used by Alembic.
revision = 'c89fea71ca43'
down_revision = 'cdbd609e2bd5'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create read_group_genomic_file association table
    Apply custom data modifications
    Drop read_group columns
    """
    op.create_table('read_group_genomic_file',
                    sa.Column('uuid', postgresql.UUID(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('modified_at', sa.DateTime(), nullable=True),
                    sa.Column('visible', sa.Boolean(), server_default='true',
                              nullable=False),
                    sa.Column('read_group_id', KfId(length=11),
                              nullable=False),
                    sa.Column('genomic_file_id', KfId(length=11),
                              nullable=False),
                    sa.Column('kf_id', KfId(length=11), nullable=False),
                    sa.ForeignKeyConstraint(['genomic_file_id'],
                                            ['genomic_file.kf_id'], ),
                    sa.ForeignKeyConstraint(['read_group_id'],
                                            ['read_group.kf_id'], ),
                    sa.PrimaryKeyConstraint('kf_id'),
                    sa.UniqueConstraint('read_group_id', 'genomic_file_id'),
                    sa.UniqueConstraint('uuid')
                    )

    op.add_column('genomic_file', sa.Column('paired_end', sa.Integer(),
                                            nullable=True))

    data_upgrades()

    op.drop_constraint('read_group_genomic_file_id_fkey', 'read_group',
                       type_='foreignkey')
    op.drop_column('read_group', 'paired_end')
    op.drop_column('read_group', 'genomic_file_id')


def data_upgrades():
    """
    COPY read_group.genomic_file_id TO read_group_genomic_file.read_group_id
    COPY read_group.kf_id TO read_group_genomic_file.read_group_id
    """
    connection = op.get_bind()

    read_group_genomic_file = sa.Table(
        'read_group_genomic_file',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11), default=kf_id_generator('RF')),
        sa.Column('genomic_file_id', KfId(length=11)),
        sa.Column('read_group_id', KfId(length=11)),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('modified_at', sa.DateTime(), default=datetime.now),
        sa.Column('uuid', postgresql.UUID(), nullable=True,
                  default=uuid_generator)
    )

    read_group = sa.Table(
        'read_group',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11)),
        sa.Column('genomic_file_id', KfId(length=11))
    )

    results = connection.execute(sa.select([
        read_group.c.genomic_file_id,
        read_group.c.kf_id
    ])).fetchall()

    for gf, rg in results:
        if not gf or not rg:
            continue
        connection.execute(read_group_genomic_file.insert().values(
            genomic_file_id=gf,
            read_group_id=rg))


def data_downgrades():
    """
    COPY read_group_genomic_file.genomic_file_id TO read_group.genomic_file_id
    # NB This will lose all information relating many files to one read_group
    """

    connection = op.get_bind()

    read_group_genomic_file = sa.Table(
        'read_group_genomic_file',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11), default=kf_id_generator('RF')),
        sa.Column('genomic_file_id', KfId(length=11)),
        sa.Column('read_group_id', KfId(length=11)),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('modified_at', sa.DateTime(), default=datetime.now),
        sa.Column('uuid', postgresql.UUID(), nullable=True,
                  default=uuid_generator)
    )

    read_group = sa.Table(
        'read_group',
        sa.MetaData(),
        sa.Column('kf_id', KfId(length=11)),
        sa.Column('genomic_file_id', KfId(length=11)),
    )

    results = connection.execute(sa.select([
        read_group_genomic_file.c.genomic_file_id,
        read_group_genomic_file.c.read_group_id,
    ])).fetchall()

    for gf, rg in results:
        if not gf or not rg:
            continue
        connection.execute(
            read_group.update().where(read_group.c.kf_id == rg).values(
                genomic_file_id=gf
            ))


def downgrade():
    """
    Reverse changes from upgrade()
    """
    op.add_column('read_group', sa.Column('genomic_file_id', sa.VARCHAR(
        length=11), autoincrement=False, nullable=True))
    op.add_column('read_group', sa.Column(
        'paired_end', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('read_group_genomic_file_id_fkey', 'read_group',
                          'genomic_file', ['genomic_file_id'], ['kf_id'],
                          ondelete='CASCADE')
    data_downgrades()

    op.alter_column('read_group', 'genomic_file_id',
                    existing_type=sa.VARCHAR(length=11),
                    nullable=True)

    op.drop_column('genomic_file', 'paired_end')
    op.drop_table('read_group_genomic_file')
