import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    HOST = "0.0.0.0"
    SSL_DISABLE = os.environ.get("SSL_DISABLE", False)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PG_HOST = os.environ.get('PG_HOST', 'localhost')
    PG_PORT = os.environ.get('PG_PORT', 5432)
    PG_NAME = os.environ.get('PG_NAME', 'dev')
    PG_USER = os.environ.get('PG_USER', 'postgres')
    PG_PASS = os.environ.get('PG_PASS', '')
    SQLALCHEMY_DATABASE_URI = 'postgres://{}:{}@{}:{}/{}'.format(
        PG_USER, PG_PASS, PG_HOST, PG_PORT, PG_NAME)

    # Default number of results per request
    DEFAULT_PAGE_LIMIT = 10
    # Determines the maximum number of results per request
    MAX_PAGE_LIMIT = 100

    INDEXD_URL = os.environ.get('INDEXD_URL', None)
    INDEXD_USER = os.environ.get('INDEXD_USER', 'test')
    INDEXD_PASS = os.environ.get('INDEXD_PASS', 'test')

    GEN3_URL = os.environ.get('GEN3_URL', 'gen3')

    BUCKET_SERVICE_URL = os.environ.get('BUCKET_SERVICE_URL', None)
    BUCKET_SERVICE_TOKEN = os.environ.get('BUCKET_SERVICE_TOKEN', None)
    SNS_EVENT_ARN = os.environ.get('SNS_EVENT_ARN', None)

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SSL_DISABLE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    SERVER_NAME = "localhost"
    TESTING = True
    WTF_CSRF_ENABLED = False
    # SQLALCHEMY_DATABASE_URI = 'postgres://postgres@localhost:5432/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    INDEXD_URL = os.environ.get('INDEXD_URL', '')
    BUCKET_SERVICE_URL = os.environ.get('BUCKET_SERVICE_URL', '')
    BUCKET_SERVICE_TOKEN = 'test123'

    MODEL_VERSION = '0.1.0'
    MIGRATION = 'aaaaaaaaaaaa'
    SNS_EVENT_ARN = None


class ProductionConfig(Config):
    pass


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "unix": UnixConfig,

    "default": DevelopmentConfig
}
