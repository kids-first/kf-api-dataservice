from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.sequencing_experiment.models import SequencingExperiment


class Aliquot(db.Model, Base):
    """
    Aliquot entity.
    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sample by contributor
    :param shipment_origin : The origin of the shipment
    :param shipment_destination: The destination of the shipment
    :param analyte_type:Text term that represents the kind of molecular
           specimen analyte
    :param concentration: The concentration of an analyte or aliquot extracted
     from the sample or sample portion, measured in milligrams per milliliter
    :param volume: The volume in microliters (ml) of the aliquots derived from
     the analyte(s) shipped for sequencing and characterization
    :param shipment_date: The date item was shipped in YYYY-MM-DD format
    """
    __tablename__ = "aliquot"
    external_id = db.Column(db.Text())
    shipment_origin = db.Column(db.Text())
    shipment_destination = db.Column(db.Text())
    analyte_type = db.Column(db.Text(), nullable=False)
    concentration = db.Column(db.Integer())
    volume = db.Column(db.Float())
    shipment_date = db.Column(db.DateTime())
    sequencing_experiments = db.relationship(SequencingExperiment,
                                             backref='sequencing_experiments',
                                             cascade="all, delete-orphan")
    sample_id = db.Column(db.String(8),
                          db.ForeignKey('sample.kf_id'), nullable=False)
