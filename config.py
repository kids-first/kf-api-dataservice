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
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres@localhost:5432/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


    INDEXD_URL = os.environ.get('INDEXD_URL', '')
    BUCKET_SERVICE_URL = os.environ.get('BUCKET_SERVICE_URL', '')
    BUCKET_SERVICE_TOKEN = 'test123'

    MODEL_VERSION = '0.1.0'
    MIGRATION = 'aaaaaaaaaaaa'
    SNS_EVENT_ARN = None


class ProductionConfig(Config):
    @staticmethod
    def init_app(app):
        import hvac

        vault_url = os.environ.get('VAULT_URL', 'https://vault:8200/')
        # Role to authenticate with
        vault_role = os.environ.get('VAULT_ROLE', 'DataserviceRole')
        # Paths for secrets in vault
        pg_secret = os.environ.get('DB_SECRET', 'secret/postgres')
        indexd_secret = os.environ.get('INDEXD_SECRET', 'secret/indexd')
        bucket_token = os.environ.get('BUCKET_SERVICE_TOKEN_SECRET', None)
        bucket_url = os.environ.get('BUCKET_SERVICE_URL_SECRET', None)
        # Retrieve secrets
        client = hvac.Client(url=vault_url)
        client.auth_iam(vault_role)
        pg_secrets = client.read(pg_secret)
        indexd_secrets = client.read(indexd_secret)
        bucket_token = client.read(bucket_token) if bucket_token else None
        bucket_url = client.read(bucket_url) if bucket_url else None
        client.logout()

        # Construct postgres connection string
        pg_user = pg_secrets['data']['user']
        pg_pass = pg_secrets['data']['password']
        connection_str = 'postgres://{}:{}@{}:{}/{}'.format(
                            pg_user,
                            pg_pass,
                            Config.PG_HOST,
                            Config.PG_PORT,
                            Config.PG_NAME)

        app.config['SQLALCHEMY_DATABASE_URI'] = connection_str

        # Extract indexd auth
        app.config['INDEXD_USER'] = indexd_secrets['data']['user']
        app.config['INDEXD_PASS'] = indexd_secrets['data']['password']

        # Get the bucket service's token for auth
        if (bucket_token and
            'data' in bucket_token and
            'token' in bucket_token ['data']):
            app.config['BUCKET_SERVICE_TOKEN'] = \
                    bucket_token['data']['token']

        # Get the bucket service's url
        if (bucket_url and
            'data' in bucket_url and
            'invoke_url' in bucket_url['data']):
            # All environments use the /api stage in api gateway
            app.config['BUCKET_SERVICE_URL'] = \
                    bucket_url['data']['invoke_url'] + 'api'


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
