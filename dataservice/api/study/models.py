import requests
from sqlalchemy import event
from flask import current_app
from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.participant.models import Participant
from dataservice.api.study_file.models import StudyFile


class Study(db.Model, Base):
    """
    Study entity representing the dbGaP study.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param data_access_authority: Name of organization which governs data
    access
    :param external_id: dbGaP accession number
    :param version: dbGaP version
    :param name: Name or title of study
    :short_name: Short name for study
    :param attribution: Link to attribution prose provided by dbGaP
    :param release_status: Release status of the study
    :param biobank_name: Name of study's biobank or source of
    specimens
    :param biobank_email: Contact email for study's biobank or source of
    specimens
    :param biobank_request_link: Link to request specimens from biobank
    :param biobank_request_instructions: Instructions for requesting specimens
    from biobank
    """
    __tablename__ = 'study'
    __prefix__ = 'SD'

    data_access_authority = db.Column(db.Text(),
                                      nullable=False,
                                      default='dbGaP')

    external_id = db.Column(db.Text(), nullable=False,
                            doc='dbGaP accession number')
    version = db.Column(db.Text(),
                        doc='dbGaP version')
    name = db.Column(db.Text(),
                     doc='Name or title of study')
    program = db.Column(
        db.Text(),
        doc='The project/program the study is a part of'
    )
    domain = db.Column(
        db.Text(),
        doc='The diagnosis domain of the study (e.g. Cancer)'
    )
    short_code = db.Column(
        db.Text(),
        doc='Alphanumeric string to identify the study'
    )
    short_name = db.Column(db.Text(),
                           doc='Short name for study')
    attribution = db.Column(db.Text(),
                            doc='Link to attribution prose provided by dbGaP')
    release_status = db.Column(db.Text(),
                               doc='Release status of the study')
    biobank_name = db.Column(
        db.Text(),
        doc='Name of study biobank or source of specimens'
    )
    biobank_email = db.Column(
        db.Text(),
        doc='Email for study biobank or source of specimens'
    )
    biobank_request_link = db.Column(
        db.Text(),
        doc='Link to request specimens from study biobank'
    )
    biobank_request_instructions = db.Column(
        db.Text(),
        doc='Instructions for requesting specimens from study biobank'
    )
    parent_study_id = db.Column(
        KfId(),
        doc="KF ID of the parent study",
    )

    participants = db.relationship(Participant,
                                   cascade="all, delete-orphan",
                                   backref='study')
    investigator_id = db.Column(KfId(),
                                db.ForeignKey('investigator.kf_id'))
    study_files = db.relationship(StudyFile,
                                  cascade="all, delete-orphan",
                                  backref='study')

    def __repr__(self):
        return '<Study {}>'.format(self.kf_id)


@event.listens_for(Study, 'after_insert', propagate=True)
def make_bucket(mapper, connection, target):
    """
    Invokes the new bucket service to create a bucket in s3 for this study.
    Only creates a new bucket on insertion of a study.
    Will not attempt to remove the bucket on deletion to prevent any unwanted
    data loss.
    """
    url = current_app.config['BUCKET_SERVICE_URL']
    if url is not None:
        header = {}
        token = current_app.config['BUCKET_SERVICE_TOKEN']
        if token:
            header['Authorization'] = 'Bearer {}'.format(token)
        resp = requests.post(url+'/buckets',
                             json={'study_id': target.kf_id},
                             headers=header)
