from marshmallow_sqlalchemy import field_for

from dataservice.api.sequencing_experiment.models import SequencingExperiment
from dataservice.api.common.schemas import BaseSchema
from dataservice.api.common.custom_fields import DateOrDatetime
from dataservice.api.common.validation import validate_positive_number
from dataservice.extensions import ma


class SequencingExperimentSchema(BaseSchema):
    sequencing_center_id = field_for(SequencingExperiment,
                                     'sequencing_center_id',
                                     required=True,
                                     load_only=True)

    class Meta(BaseSchema.Meta):
        resource_url = 'api.sequencing_experiments'
        collection_url = 'api.sequencing_experiments_list'
        model = SequencingExperiment

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
    experiment_date = DateOrDatetime(allow_none=True)

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'sequencing_center': ma.URLFor('api.sequencing_centers',
                                       kf_id='<sequencing_center_id>')
    }, description='Resource links and pagination')
