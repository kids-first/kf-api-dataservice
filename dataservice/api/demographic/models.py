from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class Demographic(db.Model, Base):
    """
    Demographic entity.

    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to demographic by contributor
    :param race: Race of participant
    :param ethnicity: Ethnicity of participant
    :param gender: Self reported gender of participant
    """
    __tablename__ = 'demographic'
    __prefix__ = 'DM'
    external_id = db.Column(db.Text(),
                            doc='Identifier used by external systems')
    race = db.Column(db.Text(),
                     doc='The race of the participant')
    ethnicity = db.Column(db.Text(),
                          doc='The ethnicity of the participant')
    gender = db.Column(db.Text(),
                       doc='The gender of the participant')
    participant_id = db.Column(KfId,
                               db.ForeignKey('participant.kf_id'),
                               nullable=False,
                               unique=True,
                               doc='kf_id of the participant this demographic'
                                   ' describes')
