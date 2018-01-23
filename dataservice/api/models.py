from datetime import datetime
from flask_restplus import Model, fields

base_fields = Model('Person', {
    'kf_id': fields.String(
        example='KF00001',
        description='ID assigned by Kids First'),
    'created_at': fields.String(
        example=datetime.now().isoformat(),
        description='Date Person was registered in with the DCC'),
    'modified_at': fields.String(
        example=datetime.now().isoformat(),
        description='Date of last update to the Persons data')
})

pagination = Model('Pagination', {
    'status': fields.Integer(
        description='HTTP response status code',
        example=200),
    'message': fields.String(
        description='Additional information about the response',
        example='Success')
})
