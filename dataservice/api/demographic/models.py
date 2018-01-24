from dataservice.extensions import db
from dataservice.api.common.model import Base


class Demographic(db.Model, Base):
    """
    Demographic entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to demographic by contributor
    :param race: race of participant
    :param ethnicity: ethnicity of participant
    :param gender: gender of participant
    :param sex: sex of participant
    """

    __tablename__ = 'demographic'
    external_id = db.Column(db.Text)
    race = db.Column(db.Text)
    ethnicity = db.Column(db.Text)
    gender = db.Column(db.Text)
    sex = db.Column(db.Text)
    participant_id = db.Column(db.String(8),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False, unique=True)
