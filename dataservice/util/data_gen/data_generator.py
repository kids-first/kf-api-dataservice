from dataservice import create_app
from dataservice.extensions import db
from dataservice.api.participant.models import Participant


class DataGenerator(object):

    def __init__(self, config_name='testing'):
        self.setup(config_name)

    def setup(self, config_name):
        self.app = create_app(config_name)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def teardown(self):
        db.session.remove()
        self.app_context.pop()

    def drop_all(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_and_publish_all(self):

        # Create participant
        p = self.create_participants()

        db.session.add(p)
        db.session.commit()
        self.teardown()

    def create_participants(self):
        p = Participant()
        return p


if __name__ == '__main__':
    d = DataGenerator()
