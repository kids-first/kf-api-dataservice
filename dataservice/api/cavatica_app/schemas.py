from marshmallow_sqlalchemy import field_for
from marshmallow.validate import URL

from dataservice.api.cavatica_app.models import CavaticaApp
from dataservice.api.common.schemas import BaseSchema
from dataservice.extensions import ma
from dataservice.api.common.validation import validate_positive_number


class CavaticaAppSchema(BaseSchema):

    revision = field_for(CavaticaApp, 'revision',
                         validate=validate_positive_number)
    github_commit_url = field_for(CavaticaApp, 'github_commit_url',
                                  validate=URL())

    class Meta(BaseSchema.Meta):
        model = CavaticaApp
        resource_url = 'api.cavatica_apps'
        collection_url = 'api.cavatica_apps_list'

    _links = ma.Hyperlinks({
        'self': ma.URLFor(Meta.resource_url, kf_id='<kf_id>'),
        'collection': ma.URLFor(Meta.collection_url)
    })
