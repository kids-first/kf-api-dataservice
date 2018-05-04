from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class CavaticaTask(db.Model, Base):
    """
    CavaticaTask entity represents an executed Cavatica task

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param name: Name of cavatica_task
    :param external_cavatica_task_id: Id of executed task assigned by Cavatica
    """
    __tablename__ = 'cavatica_task'
    __prefix__ = 'CT'

    external_cavatica_task_id = db.Column(UUID(as_uuid=True),
                                          doc='Id assigned to Cavatica task'
                                          'by Cavatica')
    name = db.Column(db.Text(), doc='Name given to Cavatica task by user')

    cavatica_app_id = db.Column(KfId(),
                                db.ForeignKey('cavatica_app.kf_id'),
                                doc='Id for the Cavatica app to which this '
                                'task belongs')

    genomic_files = association_proxy(
        'cavatica_task_genomic_files', 'genomic_file',
        creator=lambda genomic_file:
        CavaticaTaskGenomicFile(genomic_file=genomic_file,
                                is_input=genomic_file.is_harmonized))

    cavatica_task_genomic_files = db.relationship('CavaticaTaskGenomicFile',
                                                  backref='cavatica_task',
                                                  cascade='all, delete-orphan')


class CavaticaTaskGenomicFile(db.Model, Base):
    """
    Represents association table between cavatica_task table and
    genomic_file table. Contains all cavatica_task, genomic_file combiniations.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param is_input: Denotes whether the genomic file was an input to the
    executed cavatica_task. True = Input, False = Output
    """

    __tablename__ = 'cavatica_task_genomic_file'
    __prefix__ = 'CG'
    __table_args__ = (db.UniqueConstraint('genomic_file_id',
                                          'cavatica_task_id',
                                          'is_input'),)
    genomic_file_id = db.Column(KfId(),
                                db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)

    cavatica_task_id = db.Column(KfId(),
                                 db.ForeignKey('cavatica_task.kf_id'),
                                 nullable=False)
    is_input = db.Column(db.Boolean(), nullable=False, default=True)
