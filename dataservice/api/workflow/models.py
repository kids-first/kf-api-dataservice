from sqlalchemy.ext.associationproxy import association_proxy

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.genomic_file.models import GenomicFile


class Workflow(db.Model, Base):
    """
    Workflow entity represents an executed bioinformatics pipeline

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to workflow by contributor
    :param task_id: Id of executed task
    :param name: Name of workflow
    :param version: Version of workflow
    :param github_url: URL to repository hosted on GitHub
    """
    __tablename__ = 'workflow'
    __prefix__ = 'WF'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    task_id = db.Column(db.Text())
    name = db.Column(db.Text())
    github_commit_url = db.Column(db.Text())

    genomic_files = association_proxy(
        'workflow_genomic_files', 'genomic_file',
        creator=lambda genomic_file:
        WorkflowGenomicFile(genomic_file=genomic_file))


class WorkflowGenomicFile(db.Model, Base):
    """
    Represents association table between workflow table and genomic_file table.
    Contains all workflow, genomic_file combiniations.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param is_input: Denotes whether the genomic file was an input to the
    executed workflow. True = Input, False = Output
    """

    __tablename__ = 'workflow_genomic_file'
    __prefix__ = 'WG'
    __table_args__ = (db.UniqueConstraint('genomic_file_id', 'workflow_id',
                                          'is_input'),)
    genomic_file_id = db.Column(KfId(),
                                db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)

    workflow_id = db.Column(KfId(),
                            db.ForeignKey('workflow.kf_id'),
                            nullable=False)
    is_input = db.Column(db.Boolean(), nullable=False, default=False)

    genomic_file = db.relationship(
        GenomicFile,
        backref=db.backref('workflow_genomic_files',
                           cascade='all, delete-orphan'))

    workflow = db.relationship(
        Workflow,
        backref=db.backref('workflow_genomic_files',
                           cascade='all, delete-orphan'))

    def __repr__(self):
        return '<Workflow {} GenomicFile {}> is_input {}'.format(
            self.workflow.kf_id,
            self.genomic_file.kf_id,
            self.is_input)
