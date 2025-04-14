from sqlalchemy import event
from sqlalchemy.ext.associationproxy import association_proxy

from dataservice.extensions import db
from dataservice.api.common.model import Base, KfId


class SequencingExperiment(db.Model, Base):
    """
    SequencingExperiment entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_id: Name given to sequencing experiment by contributor
    :param experiment_date : Date of the sequencing experiment conducted
    :param experiment_strategy: Text term that represents the library strategy
    :param library_name: Text term that represents the name of the library
    :param library_strand: Text term that represents the library stranded-ness
    :param is_paired_end: Boolean term specifies whether reads have paired end
    :param platform: Name of the platform used to obtain data
    :param instrument_model: Text term that represents the model of instrument
    :param max_insert_size: Maximum size of the fragmented DNA
    :param mean_insert_size: Mean size of the fragmented DNA
    :param mean_depth: (Coverage)Describes the amount of sequence data that
           is available per position in the sequenced genome territory
    :param total_reads: Total reads of the sequencing experiment
    :param mean_read_length: Mean lenth of the reads
    :param target_capture_kit: Identifies the specific target capture kit
    utilized. Can be either the production-level kit name or a file path
    :param read_pair_number: Indicates whether a FASTQ file contains forward
    (R1) or reverse (R2) reads for paired-end sequencing
    :param is_adapter_trimmed: Indicates whether the FASTQ file has undergone
    adapter trimming
    :param adapter_sequencing: Specifies the base sequence of the sequencing adapter
    :param sequencing_mode: Specifies the modes of sequencing technology
    :param end_bias: The end of the cDNA molecule that is preferentially sequenced
    :param library_construction: The library construction method that was used
    :param umi_barcode_read: The type of read that contains the UMI barcode
    :param umi_barcode_offset: The offset in sequence of the UMI identifying barcode
    :param umi_barcode_size: The size of the UMI identifying barcode
    :param cell_barcode_read: The type of read that contains the cell barcode
    :param cell_barcode_offset: The offset in sequence of the cell identifying barcode
    :param cell_barcode_size: The size of the cell identifying barcode
    :param cdna_read: The type of read that contains the cDNA read
    :param cdna_read_offset: The offset in sequence for the cDNA read
    :param target_cell_number: The target number of cells per experiment or library
    :param proteomics_experiment: The type of omics experiment that the sample was subject to
    :param mass_spec_rawfile_conversion: Method of converting raw spectra files to XML-based format if applicable
    :param acquisition_type: Data acquisition type
    :param ion_fragmentation: Reporter ion MS level
    :param enrichment_approach: Enrichment method used for phospho, ubiquitin, acetyl, or other enrichment
    :param quantification_technique: Approach used for peptide quantification
    :param quantification_labeling_method: Method used for labeling or NA if label-free
    :param quantification_label_id: Specific label used or NA if label-free
    :param chromatography_approach: Column type used for liquid chromatography
    :param fractionation_approach: Method used to fractionate sample
    :param fraction_number: Number of fractions generated for sample
    """
    __tablename__ = 'sequencing_experiment'
    __prefix__ = 'SE'

    external_id = db.Column(db.Text(), nullable=False,
                            doc='Name given to sequencing experiment by'
                            ' contributor')
    experiment_date = db.Column(db.DateTime(),
                                doc='Date of the sequencing experiment'
                                ' conducted')
    experiment_strategy = db.Column(db.Text(), nullable=False,
                                    doc='Text term that represents the'
                                    ' Library strategy')
    library_name = db.Column(db.Text(),
                             doc='Text term that represents the name of the'
                             ' library')
    library_strand = db.Column(db.Text(),
                               doc='Text term that represents the'
                               ' library stranded-ness')
    library_selection = db.Column(db.Text(),
                                  doc='Text term that describes the library '
                                  'selection method')
    library_prep = db.Column(db.Text(),
                             doc='Text term that describes the library '
                             'preparation method')
    is_paired_end = db.Column(db.Boolean(), nullable=False,
                              doc='Boolean term specifies whether reads have'
                              ' paired end')
    platform = db.Column(db.Text(), nullable=False,
                         doc='Name of the platform used to obtain data')
    instrument_model = db.Column(db.Text(),
                                 doc='Text term that represents the model of'
                                 ' instrument')
    max_insert_size = db.Column(db.Integer(),
                                doc='Maximum size of the fragmented DNA')
    mean_insert_size = db.Column(db.Float(),
                                 doc='Mean size of the fragmented DNA')
    mean_depth = db.Column(db.Float(),
                           doc='Mean depth or coverage describes the amount of'
                           ' sequence data that is available per position in'
                           ' the sequenced genome territory')
    total_reads = db.Column(db.BigInteger(),
                            doc='Total reads of the sequencing experiment')
    mean_read_length = db.Column(db.Float(),
                                 doc='Mean lenth of the reads')
    target_capture_kit = db.Column(
        db.Text(),
        doc='Identifies the specific target capture kit utilized. Can be'
        ' either the production-level kit name or a file path'
    )
    read_pair_number = db.Column(
        db.Text(),
        doc='Identifies the specific target capture kit utilized. Can be'
        ' either the production-level kit name or a file path'
    )
    is_adapter_trimmed = db.Column(
        db.Boolean(),
        doc='Indicates whether the FASTQ file has undergone adapter trimming'
    )
    adapter_sequencing = db.Column(
        db.Text(),
        doc='Specifies the base sequence of the sequencing adapter'
    )


    sequencing_mode = db.Column(
        db.Text(),
        doc='The modes of sequencing technolog'
    )
    end_bias = db.Column(
        db.Text(),
        doc='The end of the cDNA molecule that is preferentially sequenced'
    )
    library_construction = db.Column(
        db.Text(),
        doc='The library construction method (including version) that was used'
    )
    umi_barcode_read = db.Column(
        db.Text(),
        doc='The type of read that contains the UMI barcode'
    )
    umi_barcode_offset = db.Column(
        db.Integer(),
        doc='The offset in sequence of the UMI identifying barcode'
    )
    umi_barcode_size = db.Column(
        db.Integer(),
        doc='The size of the UMI identifying barcode'
    )
    cell_barcode_read = db.Column(
        db.Text(),
        doc='The type of read that contains the cell barcode'
    )
    cell_barcode_offset = db.Column(
        db.Integer(),
        doc='The offset in sequence of the cell identifying barcode'
    )
    cell_barcode_size = db.Column(
        db.Integer(),
        doc='The size of the cell identifying barcode'
    )
    cdna_read = db.Column(
        db.Text(),
        doc='The type of read that contains the cDNA read'
    )
    cdna_read_offset = db.Column(
        db.Integer(),
        doc='The offset in sequence for the cDNA read'
    )
    target_cell_number = db.Column(
        db.Integer(),
        doc='The target number of cells per experiment or library'
    )
    proteomics_experiment = db.Column(
        db.Text(),
        doc='The type of omics experiment that the sample was subject to'
    )
    mass_spec_rawfile_conversion = db.Column(
        db.Text(),
        doc='Method of converting raw spectra files to XML-based format if applicable'
    )
    acquisition_type = db.Column(
        db.Text(),
        doc='Data acquisition type'
    )
    ion_fragmentation = db.Column(
        db.Text(),
        doc='Reporter ion MS level'
    )
    enrichment_approach = db.Column(
        db.Text(),
        doc='Enrichment method used for phospho, ubiquitin, acetyl, or other enrichment'
    )
    quantification_technique = db.Column(
        db.Text(),
        doc='Approach used for peptide quantification'
    )
    quantification_labeling_method = db.Column(
        db.Text(),
        doc='Method used for labeling or NA if label-free'
    )
    quantification_label_id = db.Column(
        db.Text(),
        doc='Specific label used or NA if label-free'
    )
    chromatography_approach = db.Column(
        db.Text(),
        doc='Column type used for liquid chromatography'
    )
    fractionation_approach = db.Column(
        db.Text(),
        doc='Method used to fractionate sample'
    )
    fraction_number = db.Column(
        db.Integer(),
        doc='Number of fractions generated for sample'
    )

    genomic_files = association_proxy(
        'sequencing_experiment_genomic_files',
        'genomic_file',
        creator=lambda gf: SequencingExperimentGenomicFile(genomic_file=gf))

    sequencing_experiment_genomic_files = db.relationship(
        'SequencingExperimentGenomicFile',
        backref='sequencing_experiment',
        cascade='all, delete-orphan')

    sequencing_center_id = db.Column(KfId(),
                                     db.ForeignKey('sequencing_center.kf_id'),
                                     nullable=False,
                                     doc='The kf_id of the sequencing center')


class SequencingExperimentGenomicFile(db.Model, Base):
    """
    Represents association table between sequencing_experiment table and
    genomic_file table. Contains all sequencing_experiment,
    genomic_file combiniations.
    :param kf_id: Unique id given by the Kid's First DCC
    :param created_at: Time of object creation
    :param modified_at: Last time of object modification
    """
    __tablename__ = 'sequencing_experiment_genomic_file'
    __prefix__ = 'SG'
    __table_args__ = (db.UniqueConstraint('sequencing_experiment_id',
                                          'genomic_file_id',),)
    sequencing_experiment_id = db.Column(
        KfId(),
        db.ForeignKey('sequencing_experiment.kf_id'),
        nullable=False)

    genomic_file_id = db.Column(KfId(),
                                db.ForeignKey('genomic_file.kf_id'),
                                nullable=False)
    external_id = db.Column(db.Text(),
                            doc='external id used by contributor')


@event.listens_for(SequencingExperimentGenomicFile, 'after_delete')
def delete_orphans(mapper, connection, state):
    q = (db.session.query(SequencingExperiment)
         .filter(
         ~SequencingExperiment.sequencing_experiment_genomic_files.any())
         )
    q.delete(synchronize_session='fetch')
