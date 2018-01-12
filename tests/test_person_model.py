from datetime import datetime
import uuid

from dataservice import db
from dataservice.model import Person

from utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test database model
    """
    def _create_person(self, external_id="Test_Person_0"):
        """
        Create person with external id
        """
        p = Person(external_id=external_id)
        db.session.add(p)
        db.session.commit()

        return p

    def _get_person(self, kf_id):
        """
        Get person by kids first id
        """
        return Person.query.filter_by(kf_id=kf_id).one_or_none()

    def test_create_person(self):
        """
        Test creation of person
        """
        dt = datetime.now()

        self._create_person('Test_Person_0')

        self.assertEqual(Person.query.count(), 1)
        new_person = Person.query.first()
        self.assertGreater(dt, new_person.created_at)
        self.assertGreater(dt, new_person.modified_at)
        self.assertEqual(len(new_person.kf_id), 36)
        self.assertIs(type(uuid.UUID(new_person.kf_id)), uuid.UUID)
        self.assertEqual(new_person.external_id, "Test_Person_0")

    def test_get_person(self):
        """
        Test retrieving a person
        """
        person = self._create_person('Test_Person_0')
        kf_id = person.kf_id

        person = self._get_person(kf_id)
        self.assertEqual(Person.query.count(), 1)
        self.assertEqual(person.external_id, "Test_Person_0")
        self.assertEqual(person.kf_id, kf_id)

    def test_person_not_found(self):
        """
        Test retrieving a person that does not exist
        """
        person = self._get_person("non_existent_id")
        self.assertEqual(person, None)

    def test_update_person(self):
        """
        Test updating a person
        """
        person = self._create_person('Test_Person_0')
        kf_id = person.kf_id

        person = self._get_person(kf_id)
        new_name = "Updated-{}".format(person.external_id)
        person.external_id = new_name
        db.session.commit()

        person = self._get_person(kf_id)
        self.assertEqual(person.external_id, new_name)
        self.assertEqual(person.kf_id, kf_id)

    def test_delete_person(self):
        """
        Test deleting a person
        """
        person = self._create_person('Test_Person_0')
        kf_id = person.kf_id

        person = self._get_person(kf_id)
        db.session.delete(person)
        db.session.commit()

        person = self._get_person(kf_id)
        self.assertEqual(person, None)