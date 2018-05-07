from dataservice.extensions import db
from dataservice.api.common.model import Base
from dataservice.api.cavatica_task.models import CavaticaTask


class CavaticaApp(db.Model, Base):
    """
    CavaticaApp entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param external_cavatica_app_id: Id given to Cavatica app by user
    :param name: Name given to Cavatica app by user
    :param revision: Revision number of the Cavatica app
    :param github_commit_url: GitHub URL to the last git commit made for app
    """
    __tablename__ = 'cavatica_app'
    __prefix__ = 'CA'

    external_cavatica_app_id = db.Column(
        db.Text(),
        doc='Id given to Cavatica app by Cavatica user')
    name = db.Column(db.Text(),
                     doc='Name given to Cavatica app by Cavatica user')
    revision = db.Column(db.Integer(),
                         doc='Revision number of the'
                         ' Cavatica app assigned by Cavatica user')
    github_commit_url = db.Column(db.Text(),
                                  doc='Link to git commit on GitHub')
    cavatica_tasks = db.relationship(CavaticaTask, backref='cavatica_app')
