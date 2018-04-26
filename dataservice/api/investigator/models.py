from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.study.models import Study


class Investigator(db.Model, Base):
    """
    Study entity representing the Investigator.

    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    :param external_id: Name given to investigator by contributor
    :param name: Name of the investigator
    :param institution: institution of the investigator
    """
    __tablename__ = 'investigator'
    __prefix__ = 'IG'

    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')
    name = db.Column(db.Text(),
                     doc='The name of the investigator')
    institution = db.Column(db.Text(),
                            doc='The name of the investigator\'s institution')
    studies = db.relationship(Study,
                              backref=db.backref('investigator',
                                                 lazy=True),
                              doc='kf_id of the studies belonging to this '
                                  'investigator')

    def __repr__(self):
        return '<Investigator {}>'.format(self.kf_id)
