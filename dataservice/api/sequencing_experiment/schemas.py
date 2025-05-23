from marshmallow_sqlalchemy import field_for
from marshmallow import (
    fields,
    validates
)

from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.custom_fields import DateOrDatetime
from dataservice.api.common.validation import (
    validate_positive_number,
    enum_validation_generator,
    validate_kf_id)
from dataservice.extensions import ma

EXPERIMENT_STRATEGY_ENUM = {'WGS', 'WXS', 'RNA-Seq', 'miRNA-Seq',
                            'Linked-Read WGS (10x Chromium)',
                            'Targeted Sequencing', 'Methylation',
                            'Panel', 'scRNA-Seq', 'snRNA-Seq', 'Other',
                            'snATAC-Seq', 'Proteomics',
                            'Circular Consensus Sequencing RNA-Seq',
                            'Circular Consensus Sequencing WGS',
                            'Continuous Long Reads RNA-Seq',
                            'Continuous Long Reads WGS',
                            'ONT WGS'}
PLATFORM_ENUM = {'DNBSEQ', 'Illumina', 'SOLiD', 'LS454', 'Ion Torrent',
                 'Complete Genomics', 'PacBio', 'ONT', 'Other',
                 'Illumina Infinium HumanMethylation450',
                 'Illumina Infinium HumanMethylationEPIC',
                 'Illumina Infinium HumanMethylationEPICv2',
                 'Illumina Infinium HumanMethylation27k',
                 'Roche NimbleGen MethylationSeq',
                 'Agilent SurePrint Methyl-Seq',
                 'Orbitrap Fusion Lumos',
                 'Q Exactive HF',
                 'Triple TOF 6600'}

LIBRARY_STRAND_ENUM = {'Stranded', 'Unstranded', 'First Stranded',
                       'Second Stranded', 'Other'}

LIBRARY_SELECTION_ENUM = {'Hybrid Selection', 'PCR', 'Affinity Enrichment',
                          'Poly-T Enrichment', 'Random', 'rRNA Depletion',
                          'miRNA Size Fractionation', 'Other'}

LIBRARY_PREP_ENUM = {'polyA', 'totalRNAseq', 'Other'}

READ_PAIR_NUMBER = {'R1', 'R2', 'Not Applicable'}
READ_ENUM = {'index1', 'index2', 'read1', 'read2', 'Not Applicable'}
SEQUENCING_MODE = {'CLR', 'CCS', 'Not Applicable'}
END_BIAS = {'3-end', '5-end', 'full-length', 'Not Applicable'}
ACQUISITION_TYPE = {'DDA', 'DIA'}


class SequencingExperimentSchema(BaseSchema):
    sequencing_center_id = field_for(SequencingExperiment,
                                     'sequencing_center_id',
                                     required=True,
                                     load_only=True)
    experiment_strategy = field_for(SequencingExperiment,
                                    'experiment_strategy',
                                    validate=enum_validation_generator(
                                        EXPERIMENT_STRATEGY_ENUM))
    platform = field_for(SequencingExperiment, 'platform',
                         validate=enum_validation_generator(
                             PLATFORM_ENUM))
    library_strand = field_for(SequencingExperiment, 'library_strand',
                               validate=enum_validation_generator(
                                   LIBRARY_STRAND_ENUM))
    library_selection = field_for(SequencingExperiment, 'library_selection',
                                  validate=enum_validation_generator(
                                      LIBRARY_SELECTION_ENUM))

    library_prep = field_for(SequencingExperiment, 'library_prep',
                             validate=enum_validation_generator(
                                 LIBRARY_PREP_ENUM))
    read_pair_number = field_for(SequencingExperiment, 'read_pair_number',
                                 validate=enum_validation_generator(
                                     READ_PAIR_NUMBER))

    sequencing_mode = field_for(SequencingExperiment, 'sequencing_mode',
                                validate=enum_validation_generator(
                                     SEQUENCING_MODE))
    end_bias = field_for(SequencingExperiment, 'end_bias',
                         validate=enum_validation_generator(
                             END_BIAS))
    umi_barcode_read = field_for(SequencingExperiment, 'umi_barcode_read',
                                 validate=enum_validation_generator(
                                     READ_ENUM))
    cell_barcode_read = field_for(SequencingExperiment, 'cell_barcode_read',
                                  validate=enum_validation_generator(
                                     READ_ENUM))
    cdna_read = field_for(SequencingExperiment, 'cdna_read',
                          validate=enum_validation_generator(
                                     READ_ENUM))
    acquisition_type = field_for(SequencingExperiment, 'acquisition_type',
                                 validate=enum_validation_generator(
                                     ACQUISITION_TYPE))

    class Meta(BaseSchema.Meta):
        resource_url = 'api.sequencing_experiments'
        collection_url = 'api.sequencing_experiments_list'
        model = SequencingExperiment
        exclude = (BaseSchema.Meta.exclude +
                   ('sequencing_center', ) +
                   ('genomic_files', ))

    max_insert_size = field_for(SequencingExperiment, 'max_insert_size',
                                validate=validate_positive_number)
    mean_insert_size = field_for(SequencingExperiment, 'mean_insert_size',
                                 validate=validate_positive_number)
    mean_depth = field_for(SequencingExperiment, 'mean_depth',
                           validate=validate_positive_number)
    total_reads = field_for(SequencingExperiment, 'total_reads',
                            validate=validate_positive_number)
    mean_read_length = field_for(SequencingExperiment, 'mean_read_length',
                                 validate=validate_positive_number)
    experiment_date = field_for(SequencingExperiment, 'experiment_date',
                                field_class=DateOrDatetime)
    umi_barcode_offset = field_for(SequencingExperiment, 'umi_barcode_offset',
                                   validate=validate_positive_number)
    umi_barcode_size = field_for(SequencingExperiment, 'umi_barcode_size',
                                 validate=validate_positive_number)
    cell_barcode_offset = field_for(SequencingExperiment,
                                    'cell_barcode_offset',
                                    validate=validate_positive_number)
    cell_barcode_size = field_for(SequencingExperiment, 'cell_barcode_size',
                                  validate=validate_positive_number)
    cdna_read_offset = field_for(SequencingExperiment, 'cdna_read_offset',
                                 validate=validate_positive_number)
    target_cell_number = field_for(SequencingExperiment, 'target_cell_number',
                                   validate=validate_positive_number)
    fraction_number = field_for(SequencingExperiment, 'fraction_number',
                                validate=validate_positive_number)

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'sequencing_center': ma.URLFor('api.sequencing_centers',
                                       kf_id='<sequencing_center_id>'),
        'sequencing_experiment_genomic_files': ma.URLFor(
            'api.sequencing_experiment_genomic_files_list',
            sequencing_experiment_id='<kf_id>'),
        'genomic_files': ma.URLFor('api.genomic_files_list',
                                   sequencing_experiment_id='<kf_id>')
    }, description='Resource links and pagination')


class SequencingExperimentFilterSchema(SequencingExperimentSchema):

    genomic_file_id = fields.Str()

    @validates('genomic_file_id')
    def valid_genomic_file_id(self, value):
        validate_kf_id('GF', value)
