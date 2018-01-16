from datetime import datetime
from flask_restplus import fields

from .resources import person_api

person_model = person_api.model('Person', {
    'kf_id': fields.String(
        example='KF00001',
        description='ID assigned by Kids First'),
    'created_at': fields.String(
        example=datetime.now().isoformat(),
        description='Date Person was registered in with the DCC'),
    'modified_at': fields.String(
        example=datetime.now().isoformat(),
        description='Date of last update to the Persons data'),
    'external_id': fields.String(
        example='SUBJ-3993',
        description='Identifier used in the original study data')
})

person_list = person_api.model("Persons", {
    "persons": fields.List(fields.Nested(person_model))
})

response_model = person_api.model('Response', {
    'content': fields.Nested(person_list),
    'status': fields.Integer(
        description='HTTP response status code',
        example=200),
    'message': fields.String(
        description='Additional information about the response',
        example='Success')
})
