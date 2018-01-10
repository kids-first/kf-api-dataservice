from datetime import datetime
from flask import request
from flask_restplus import Namespace, Resource, fields

from ... import model
from ... import db


description = open('dataservice/api/person/README.md').read()

person_api = Namespace(name='persons', description=description)


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
    'source_name': fields.String(
        example='SUBJ-3993',
        description='Identifier used in the original study data')
})

response_model = person_api.model('Response', {
    'content': fields.Nested(person_model),
    'status': fields.Integer(
        description='HTTP response status code',
        example=200),
    'message': fields.String(
        description='Additional information about the response',
        example='Success')
})


@person_api.route('/<string:person_id>')
class Person(Resource):
    @person_api.marshal_with(response_model)
    @person_api.doc(responses={201: 'person created',
                               400: 'invalid data'})
    @person_api.expect(person_model)
    def put(self, person_id):
        """
        Create a new person

        Creates a new person and assigns a Kids First id
        """
        body = request.json
        person = model.Person(**body)
        db.session.add(person)
        db.session.commit()
        return {'status': 201,
                'message': 'person created',
                'content': person}, 201

    @person_api.marshal_with(response_model)
    @person_api.doc(responses={200: 'person found',
                               404: 'person not found'})
    def get(self, person_id):
        """
        Get a person by id

        Gets a person given a Kids First id
        """
        person = model.Person.query.get_or_404(person_id)
        return {'status': 200,
                'message': 'person found',
                'content': person}, 200

    def delete(self, person_id):
        """
        Delete person by id

        Deletes a person given a Kids First id
        """
        person = model.Person.query.get_or_404(person_id)
        return {'status': 200,
                'message': 'deleted'}, 200
