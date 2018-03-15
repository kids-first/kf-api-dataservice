from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, Model
from flask_marshmallow import Marshmallow
from dataservice.extensions.flask_indexd import Indexd

db = SQLAlchemy()
ma = Marshmallow()
indexd = Indexd()

migrate = Migrate()
