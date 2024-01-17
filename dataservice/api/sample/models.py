from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.container.models import Container
from sqlalchemy import event


class Sample(db.Model, Base):
    """
    Sample entity

    This table is being added in order to represent the Sample, Container
    concepts and their parent child relationship without affecting the
    current Biospecimen entity. The Container can be thought of as
    synonymous with Biospecimen.

    The Sample represents a group of biologically equivalent biospecimens/
    containers

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sample by contributor
    :param sample_event_key: An identifier that represents when the sample 
    was drawn
    :param composition : The cellular composition of the sample.
    :param tissue_type: description of the kind of tissue collected
           with respect to disease status or proximity to tumor tissue
    :param anatomical_location : The name of the primary disease site
           of the submitted tumor sample
    :param analyte_type: Text term that represents the kind of molecular
           specimen analyte
    :param concentration_mg_per_ml: The concentration of an analyte or aliquot
           extracted from the sample or sample portion, measured in
           milligrams per milliliter
    :param volume_ul: The volume in microliters (ul) of the aliquots derived
           from the analyte(s) shipped for sequencing and characterization
    :param preservation_method: Text term that represents the method used
           to preserve the sample
    :param method_of_sample_procurement: Text term that represents the method
           used to extract the analytes from the sample 
    """

    __tablename__ = 'sample'
    __prefix__ = 'SA'

    external_id = db.Column(
        db.Text(),
        doc='Name given to sample by contributor'
    )
    tissue_type = db.Column(
        db.Text(),
        doc='Description of the kind of sample collected'
    )
    composition = db.Column(
        db.Text(),
        doc='The cellular composition of the sample'
    )
    anatomical_location = db.Column(
        db.Text(),
        doc='The anatomical location of collection'
    )
    analyte_type = db.Column(
        db.Text(),
        doc='The molecular description of the sample'
    )
    concentration_mg_per_ml = db.Column(
        db.Float(),
        doc='The concentration of the sample'
    )
    volume_ul = db.Column(
        db.Float(),
        doc='The volume of the sample'
    )
    method_of_sample_procurement = db.Column(
        db.Text(),
        doc='The method used to procure the sample used to extract '
        'analyte(s)'
    )
    preservation_method = db.Column(
        db.Text(),
        doc='Text term that represents the method used to preserve the sample'
    )
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False,
                               doc='The kf_id of the sample\'s donor')
    containers = db.relationship(Container,
                                 cascade='all, delete-orphan',
                                 backref=db.backref('sample',
                                                    lazy=True))


@event.listens_for(Container, 'after_delete')
def delete_orphans(mapper, connection, state):
    q = (db.session.query(Sample)
         .filter(~Sample.containers.any()))
    q.delete(synchronize_session='fetch')
