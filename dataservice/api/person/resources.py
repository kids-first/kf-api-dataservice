from datetime import datetime
from flask import request
from flask_restplus import Namespace, Resource, fields, abort

from dataservice import db
from . import models

description = open('dataservice/api/person/README.md').read()

person_api = Namespace(name='persons', description=description)

from .serializers import (person_model,
                          response_model)


@person_api.route('/')
class PersonList(Resource):
    @person_api.marshal_with(response_model)
    def get(self):
        """
        Get all persons
        """
        persons = models.Person.query.all()
        return {'status': 200,
                'message': '{} persons'.format(len(persons)),
                'content': {'persons': persons}}, 200

    @person_api.marshal_with(response_model)
    @person_api.doc(responses={201: 'person created',
                               400: 'invalid data'})
    @person_api.expect(person_model)
    def post(self):
        """
        Create a new person

        Creates a new person and assigns a Kids First id
        """
        body = request.json
        person = models.Person(**body)
        db.session.add(person)
        db.session.commit()
        return {'status': 201,
                'message': 'person created',
                'content': {'persons': [person]}}, 201


@person_api.route('/<string:kf_id>')
class Person(Resource):
    @person_api.marshal_with(response_model)
    @person_api.doc(responses={200: 'person found',
                               404: 'person not found'})
    def get(self, kf_id):
        """
        Get a person by id
        Gets a person given a Kids First id
        """
        person = models.Person.query.filter_by(kf_id=kf_id).one_or_none()
        if not person:
            self._not_found(kf_id)

        return {'status': 200,
                'message': 'person found',
                'content': {'persons': [person]}}, 200

    @person_api.marshal_with(response_model)
    @person_api.doc(responses={201: 'person updated',
                               400: 'invalid data',
                               404: 'person not found'})
    @person_api.expect(person_model)
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

        return {'status': 201,
                'message': 'person updated',
                'content': {'persons': [person]}}, 201

    @person_api.marshal_with(response_model)
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
        return {'status': 200,
                'message': 'person deleted',
                'content': {'persons': [person]}}, 200

    def _not_found(self, kf_id):
        """
        Temporary helper - will do error handling better later
        """
        status = 404
        abort(status, "Person with kf_id '{}' not found".format(kf_id),
              status=status, content=None)
