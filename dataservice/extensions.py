from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, Model


db = SQLAlchemy()

migrate = Migrate()
