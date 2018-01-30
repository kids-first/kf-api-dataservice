from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.genomic_file.models import GenomicFile


class SequencingExperiment(db.Model, Base):
    """
    SequencingExperiment entity.
    :param _id: Unique id assigned by RDBMS
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to SequencingExperiment by contributor
    :param experiment_date : The origin of the shipment
    :param experiment_strategy: Text term that represents the Library strategy
    :param center:Text term that represents the sequencing center
    :param library_name: Text term that represents the name of the library
    :param library_strand: Text term that represents the library stranded-ness
    :param is_paired_end: Boolean term specifies whether reads have paired end
    :param platform: Name of the platform used to obtain data
    :param instrument_model:Text term that represents the model of instrument
    :param max_insert_size: Maximum size of the fragmented DNA
    :param mean_insert_size: Mean size of the fragmented DNA
    :param mean_depth:(Coverage)Describes the amount of sequence data that
           is available per position in the sequenced genome territory
    :param total_reads: total reads
    :param mean_read_length: mean lenth of the reads
    """
    __tablename__ = "sequencing_experiment"
    external_id = db.Column(db.Text(), nullable=False)
    experiment_date = db.Column(db.DateTime())
    # WGS,WXS
    experiment_strategy = db.Column(db.Text(), nullable=False)
    center = db.Column(db.Text(), nullable=False)
    library_name = db.Column(db.Text())
    # Unstranded
    library_strand = db.Column(db.Text())
    is_paired_end = db.Column(db.Boolean(), nullable=False)
    platform = db.Column(db.Text(), nullable=False)
    # 454 GS FLX Titanium
    instrument_model = db.Column(db.Text())
    max_insert_size = db.Column(db.Integer())
    mean_insert_size = db.Column(db.Float())
    mean_depth = db.Column(db.Float())
    total_reads = db.Column(db.Integer())
    mean_read_length = db.Column(db.Float())
    aliquot_id = db.Column(db.String(8),
                           db.ForeignKey('aliquot.kf_id'), nullable=False)
    genomic_files = db.relationship(GenomicFile,
                                    cascade="all, delete-orphan",
                                    backref=db.backref(
                                        'sequencing_experiments',
                                        lazy=True))
