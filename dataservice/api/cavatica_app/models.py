from dataservice.extensions import db
from dataservice.api.common.model import Base


class CavaticaApp(db.Model, Base):
    """
    CavaticaApp entity.
    :param kf_id: Unique id given by the Kid's First DCC
    :param name: Name given to Cavatica app by user
    :param revision: Revision number of the Cavatica app
    :param github_commit_url: URL to the git commit on GitHub
    """
    __tablename__ = 'cavatica_app'
    __prefix__ = 'CA'

    cavatica_app_id = db.Column(db.Text(),
                                doc='Id generated by Cavatica for app')
    name = db.Column(db.Text(),
                     doc='Name given to Cavatica app by Cavatica user')
    revision = db.Column(db.Integer(),
                         doc='Revision number of the'
                         ' Cavatica app by Cavatica user')
    github_commit_url = db.Column(db.Text(),
                                  doc='Link to git commit on GitHub')
    cavatica_tasks = db.relationship('CavaticaTask', backref='cavatica_app')