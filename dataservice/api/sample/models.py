from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId
from dataservice.api.biospecimen.models import Biospecimen
from sqlalchemy import event

# Columns for Sample unique constraint
unique_cols = (
    "external_id",
    "participant_id",
    "age_at_event_days",
    "sample_type",
    "anatomical_location",
    "method_of_sample_procurement",
    "tissue_type",
    "preservation_method",
)
# Mapping to Biospecimen columns
col_mapping = {
    "participant_id": "participant_id",
    "external_id": "external_sample_id",
    "age_at_event_days": "age_at_event_days",
    "sample_type": "composition",
    "anatomical_location": "source_text_anatomical_site",
    "method_of_sample_procurement": "method_of_sample_procurement",
    "tissue_type": "source_text_tissue_type",
    "preservation_method": "preservation_method",
    "volume_ul": "volume_ul",
    "amount": "amount",
    "amount_unit": "amount_unit"
}


class Sample(db.Model, Base):
    """
    Sample - a biologically distinct unit

    The Biospecimen represents an aliquot or portion of a Sample

    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sample by contributor
    :param age_at_event_days: Age at the time of event occurred in number of
    days since birth
    :param sample_event_key: An identifier for the sample collection event
    :param sample_type : The cellular sample_type of the sample.
    :param tissue_type: description of the kind of tissue collected
           with respect to disease status or proximity to tumor tissue
    :param anatomical_location : The name of the primary disease site
           of the submitted tumor sample
    :param volume_ul: The volume in microliters (ul) of the aliquots derived
           from the analyte(s) shipped for sequencing and characterization
    :param amount: the amount ( in amount_units) of the aliquots derived from
           the analyte(s) shipped for sequencing and characterization
    :param amount_units: the units of the amount of the aliquots derived from
           the analyte(s) shipped for sequencing and characterization
    :param preservation_method: Text term that represents the method used
           to preserve the sample
    :param method_of_sample_procurement: Text term that represents the method
           used to extract the analytes from the sample
    :param has_matched_normal_sample: Indicates if a sample has a matched
           normal sample.
    :param external_collection_id: Identifier for the collection event
    """

    __tablename__ = 'sample'
    __prefix__ = 'SA'
    __unique_constraint__ = db.UniqueConstraint(
        *unique_cols,
        name="sample_unique_constraint"
    )
    __table_args__ = (__unique_constraint__,)

    external_id = db.Column(
        db.Text(),
        doc='Name or ID given to sample by contributor'
    )
    age_at_event_days = db.Column(db.Integer(),
                                  doc='Age at the time of event occurred in '
                                      'number of days since birth.')
    sample_event_key = db.Column(
        db.Text(),
        doc='Identifier for event when sample was first drawn'
    )
    tissue_type = db.Column(
        db.Text(),
        doc='Description of the kind of tissue collected if its a tissue type '
        'sample'
    )
    sample_type = db.Column(
        db.Text(),
        doc='The kind of material of the sample'
    )
    anatomical_location = db.Column(
        db.Text(),
        doc='The anatomical location of collection'
    )
    volume_ul = db.Column(
        db.Float(),
        doc='The volume of the sample'
    )
    amount = db.Column(db.Float(),
                       doc='The amount of the sample')
    amount_units = db.Column(db.Text(),
                             doc='The units of the amount of the sample')
    method_of_sample_procurement = db.Column(
        db.Text(),
        doc='The method used to procure the sample used to extract '
        'analyte(s)'
    )
    preservation_method = db.Column(
        db.Text(),
        doc='Text term that represents the method used to preserve the sample'
    )
    has_matched_normal_sample = db.Column(
        db.Boolean(),
        doc='Indicates if the sample has a matched normal sample'
    )
    external_collection_id = db.Column(
        db.Text(),
        doc='Identifier for the collection event'
    )
    participant_id = db.Column(KfId(),
                               db.ForeignKey('participant.kf_id'),
                               nullable=False,
                               doc='The kf_id of the sample\'s donor')
    biospecimens = db.relationship(
        Biospecimen, backref=db.backref('sample', lazy=True)
    )
