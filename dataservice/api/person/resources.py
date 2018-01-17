from flask import request
from flask_restplus import Namespace, Resource, fields, abort

from dataservice.extensions import db
from dataservice.api.person import models
from dataservice.api.common.formatters import kf_response

description = open('dataservice/api/person/README.md').read()

person_api = Namespace(name='persons', description=description)

from dataservice.api.person.serializers import (
    person_fields,
    person_list,
    person_response
)


@person_api.route('/')
class PersonList(Resource):
    @person_api.marshal_with(person_list)
    def get(self):
        """
        Get all persons

        Returns paginated persons
        """
        persons = models.Person.query.all()
        return kf_response(persons, 200, '{} persons'.format(len(persons)))

    @person_api.marshal_with(person_response)
    @person_api.doc(responses={201: 'person created',
                               400: 'invalid data'})
    @person_api.expect(person_fields)
    def post(self):
        """
        Create a new person

        Creates a new person and assigns a Kids First id
        """
        body = request.json
        person = models.Person(**body)
        db.session.add(person)
        db.session.commit()

        return kf_response(person, 201, 'person created')


@person_api.route('/<string:kf_id>')
class Person(Resource):
    @person_api.marshal_with(person_response)
    @person_api.doc(responses={200: 'person found',
                               404: 'person not found'})
    def get(self, kf_id):
        """
        Get a person by id
        Gets a person given a Kids First id
        """
        person = models.Person.query.filter_by(kf_id=kf_id).one_or_none()
        if not person:
            return self._not_found(kf_id)

        return kf_response(person, 200, 'person found')

    @person_api.marshal_with(person_response)
    @person_api.doc(responses={201: 'person updated',
                               400: 'invalid data',
                               404: 'person not found'})
    @person_api.expect(person_fields)
    def put(self, kf_id):
        """
        Update an existing person
        """
        body = request.json
        person = models.Person.query.filter_by(kf_id=kf_id).one_or_none()
        if not person:
            self._not_found(kf_id)

        person.external_id = body.get('external_id')
        db.session.commit()

        return kf_response(person, 201, 'person updated')

    @person_api.marshal_with(person_response)
    @person_api.doc(responses={204: 'person deleted',
                               404: 'person not found'})
    def delete(self, kf_id):
        """
        Delete person by id

        Deletes a person given a Kids First id
        """
        person = models.Person.query.filter_by(kf_id=kf_id).one_or_none()
        if not person:
            self._not_found(kf_id)

        db.session.delete(person)
        db.session.commit()

        return kf_response(person, 200, 'person deleted')

    def _not_found(self, kf_id):
        """
        Temporary helper - will do error handling better later
        """
        return kf_response(code=404,
                message='person with kf_id \'{}\' not found'.format(kf_id)), 404
