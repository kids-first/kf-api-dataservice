from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Task(db.Model, Base):
    """
    Task entity represents an executed informatics task

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param name: Name of the task
    :param external_task_id: Id of executed task assigned by the external
        informatics tool, eg: Cavatica or Firecloud.
    """
    __tablename__ = 'task'
    __prefix__ = 'TK'

    external_task_id = db.Column(UUID(as_uuid=True),
                                 doc='Id of the task used by external'
                                 'systems')
    name = db.Column(db.Text(), doc='Name given to the task by user')

    cavatica_app_id = db.Column(KfId(),
                                db.ForeignKey('cavatica_app.kf_id'),
                                doc='Id for the Cavatica app to which this '
                                'task belongs')

    genomic_files = association_proxy(
        'task_genomic_files', 'genomic_file',
        creator=lambda genomic_file:
        TaskGenomicFile(genomic_file=genomic_file,
                        is_input=genomic_file.is_harmonized))

    task_genomic_files = db.relationship('TaskGenomicFile',
                                         backref='task',
                                         cascade='all, delete-orphan')


class TaskGenomicFile(db.Model, Base):
    """
    Represents association table between task table and
    genomic_file table. Contains all task, genomic_file combiniations.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param is_input: Denotes whether the genomic file was an input to the
        executed task. True = Input, False = Output
    """

    __tablename__ = 'task_genomic_file'
    __prefix__ = 'TG'
    __table_args__ = (db.UniqueConstraint('genomic_file_id',
                                          'task_id',
                                          'is_input'),)
    genomic_file_id = db.Column(KfId(),
                                db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)

    task_id = db.Column(KfId(),
                        db.ForeignKey('task.kf_id'),
                        nullable=False)
    is_input = db.Column(db.Boolean(), nullable=False, default=True)
