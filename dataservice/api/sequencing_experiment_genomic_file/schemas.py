from marshmallow_sqlalchemy import field_for

from dataservice.api.sequencing_experiment.models import (
    SequencingExperimentGenomicFile
)
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma


class SequencingExperimentGenomicFileSchema(BaseSchema):

    sequencing_experiment_id = field_for(SequencingExperimentGenomicFile,
                                         'sequencing_experiment_id',
                                         required=True, load_only=True,
                                         example='SE_ABB2C104')
    genomic_file_id = field_for(SequencingExperimentGenomicFile,
                                'genomic_file_id',
                                required=True, load_only=True,
                                example='GF_ABB2C104')

    class Meta(BaseSchema.Meta):
        model = SequencingExperimentGenomicFile
        resource_url = 'api.sequencing_experiment_genomic_files'
        collection_url = 'api.sequencing_experiment_genomic_files_list'
        exclude = BaseSchema.Meta.exclude + ('sequencing_experiment',
                                             'genomic_file')

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url),
        'sequencing_experiment': ma.URLFor('api.sequencing_experiments',
                                           kf_id='<sequencing_experiment_id>'),
        'genomic_file': ma.URLFor('api.genomic_files',
                                  kf_id='<genomic_file_id>')
    })
