import unittest
from datetime import datetime
import uuid

from dataservice import db
from dataservice.model import Person

from utils import FlaskTestCase


class ModelTest(FlaskTestCase):
    """
    Test database model
    """

    def test_person(self):
        """
        Test creation of person
        """
        dt = datetime.now()

        p = Person(source_name="subject1")
        db.session.add(p)
        db.session.commit()

        self.assertEqual(Person.query.count(), 1)
        new_person = Person.query.first()
        self.assertGreater(dt, new_person.created_at)
        self.assertGreater(dt, new_person.modified_at)
        self.assertEqual(len(new_person.kf_id), 36)
        self.assertIs(type(uuid.UUID(new_person.kf_id)), uuid.UUID)
        self.assertEqual(new_person.source_name, "subject1")
