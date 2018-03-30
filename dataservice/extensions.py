from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cache import Cache


cache = Cache(config={'CACHE_TYPE': 'simple'})
db = SQLAlchemy()
ma = Marshmallow()

migrate = Migrate()
