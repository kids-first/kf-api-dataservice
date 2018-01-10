import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api
from config import config, DevelopmentConfig

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    from dataservice.api import api
    api.init_app(app)

    return app
