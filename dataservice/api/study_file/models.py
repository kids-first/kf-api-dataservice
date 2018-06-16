from dataservice.extensions import db
from dataservice.api.common.model import Base, IndexdFile, KfId, IndexdField


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
    :param availability: Indicates whether a file is available for immediate
           download, or is in cold storage
    """
    def __init__(self, *args, file_name='', urls=[], rev=None, hashes={},
                 acl=[], _metadata={}, size=None, **kwargs):
        # Fields used by indexd, but not tracked in the database
        self.file_name = IndexdField(file_name)
        self.urls = IndexdField(urls)
        self.rev = rev
        self.hashes = IndexdField(hashes)
        self.acl = IndexdField(acl)
        # The metadata property is already used by sqlalchemy
        self._metadatas = IndexdField(_metadata)
        self.size = IndexdField(size)
        return super().__init__(*args, **kwargs)

    __tablename__ = 'study_file'
    __prefix__ = 'SF'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    study_id = db.Column(KfId(),
                         db.ForeignKey('study.kf_id'),
                         nullable=False)
    availability = db.Column(db.Text(), doc='Indicates whether a file is '
                             'available for immediate download, or is in '
                             'cold storage')
    data_type = db.Column(db.Text(), doc='Type of data')
    file_format = db.Column(db.Text(), doc='Format of the file')

    def __repr__(self):
        return '<StudyFile {}>'.format(self.kf_id)
