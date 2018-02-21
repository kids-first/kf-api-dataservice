from dataservice.extensions import db
from dataservice.api.common.model import Base


class StudyFile(db.Model, Base):
    """
    StudyFile entity representing the raw files of dbGaP study.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param file_name: File name of study
    """
    __tablename__ = "study_file"
    file_name = db.Column(db.Text())
    study_id = db.Column(db.String(8),
                         db.ForeignKey('study.kf_id'),
                         nullable=False)

    def __repr__(self):
        return '<StudyFile {}>'.format(self.kf_id)
