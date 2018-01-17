from datetime import datetime
import uuid

from dataservice.extensions import db
from dataservice.api.person.models import Person
from tests.utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def test_create_person(self):
        """
        Test creation of person
        """
        dt = datetime.now()

        Person.create(external_id='Test_Person_0')

        self.assertEqual(Person.query.count(), 1)
        new_person = Person.query.first()
        self.assertGreater(new_person.created_at, dt)
        self.assertGreater(new_person.modified_at, dt)
        self.assertIs(type(uuid.UUID(new_person.uuid)), uuid.UUID)
        self.assertEqual(new_person.external_id, "Test_Person_0")

    def test_get_person(self):
        """
        Test retrieving a person
        """
        person = Person.create(external_id='Test_Person_0')
        kf_id = person.kf_id

        person = Person.find_one(kf_id=kf_id)
        self.assertEqual(Person.query.count(), 1)
        self.assertEqual(person.external_id, "Test_Person_0")
        self.assertEqual(person.kf_id, kf_id)

    def test_person_not_found(self):
        """
        Test retrieving a person that does not exist
        """
        person = Person.find_one(kf_id='non-existent id')
        self.assertEqual(person, None)

    def test_update_person(self):
        """
        Test updating a person
        """
        person = Person.create(external_id='Test_Person_0')
        kf_id = person.kf_id

        person = Person.find_one(kf_id=kf_id)
        new_name = "Updated-{}".format(person.external_id)
        person.external_id = new_name
        db.session.commit()

        person = Person.find_one(kf_id=kf_id)
        self.assertEqual(person.external_id, new_name)
        self.assertEqual(person.kf_id, kf_id)

    def test_delete_person(self):
        """
        Test deleting a person
        """
        person = Person.create(external_id='Test_Person_0')
        kf_id = person.kf_id

        person = Person.find_one(kf_id=kf_id)
        person.delete()

        person = Person.find_one(kf_id=kf_id)
        self.assertEqual(person, None)
