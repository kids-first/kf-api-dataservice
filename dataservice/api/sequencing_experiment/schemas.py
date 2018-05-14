from marshmallow_sqlalchemy import field_for

from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.custom_fields import DateOrDatetime
from dataservice.api.common.validation import (validate_positive_number,
                                               enum_validation_generator)
from dataservice.extensions import ma

EXPERIMENT_STRATEGY_ENUM = {'WGS', 'WXS', 'RNA-Seq', 'miRNA-Seq', 'Other'}
PLATFORM_ENUM = {'Illumina', 'SOLiD', 'LS454', 'Ion Torrent',
                 'Complete Genomics', 'PacBio', 'Other'}
LIBRARY_STRAND_ENUM = {'Unstranded', 'First Stranded',
                       'Second Stranded', 'Other'}


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

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'sequencing_center': ma.URLFor('api.sequencing_centers',
                                       kf_id='<sequencing_center_id>'),
        'genomic_files': ma.URLFor('api.genomic_files_list',
                                   sequencing_experiment_id='<kf_id>')
    }, description='Resource links and pagination')
