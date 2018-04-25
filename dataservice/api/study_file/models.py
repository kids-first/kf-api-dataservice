from dataservice.extensions import db
from dataservice.api.common.model import Base, IndexdFile, KfId


class StudyFile(db.Model, Base, IndexdFile):
    """
    StudyFile entity representing the raw files of dbGaP study.

    :param kf_id: Unique id given by the Kid's First DCC
    :param uuid: The baseid assigned to the file by indexd
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to study_file by contributor
    :param file_name: Name of the study file
    :param latest_did: UUID for the latest version of the file in indexd
    :param urls: Locations of file
    :param hashes: A dict keyed by hash type containing hashes of the file
    :param _metadata: A dict with any additional information
    :param controlled_access: whether or not the file is controlled access
    """
    __tablename__ = 'study_file'
    __prefix__ = 'SF'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    study_id = db.Column(KfId(),
                         db.ForeignKey('study.kf_id'),
                         nullable=False)
    data_type = db.Column(db.Text(), doc='Type of data')
    file_format = db.Column(db.Text(), doc='Format of the file')

    def __repr__(self):
        return '<StudyFile {}>'.format(self.kf_id)
