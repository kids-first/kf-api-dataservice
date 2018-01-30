import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    HOST = "0.0.0.0"
    SSL_DISABLE = os.environ.get("SSL_DISABLE", False)

    RESTPLUS_MASK_SWAGGER = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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


class ProductionConfig(Config):
    @staticmethod
    def init_app(app):
        import hvac

        vault_url = os.environ.get('VAULT_URL', 'https://vault:8200/')
        # Role to authenticate with
        iam_role = os.environ.get('IAM_ROLE', 'PostgresRole')
        # Path for the postgres secret in vault
        pg_secret = os.environ.get('DB_SECRET', 'secret/postgres')

        # Retrieve postgres secrets
        client = hvac.Client(url=vault_url)
        client.auth_iam(iam_role)
        secrets = client.read(pg_secret)
        client.logout()

        pg_host = os.environ.get('PG_HOST', 'localhost')
        pg_name = os.environ.get('PG_NAME', 'prod')
        pg_user = secrets['data']['username']
        pg_pass = secrets['data']['password']

        connection_str = 'postgres://{}:{}@{}:{}/{}'.format(
                            pg_user,
                            pg_pass,
                            Config.PG_HOST,
                            Config.PG_PORT,
                            Config.PG_NAME)

        app.config['SQLALCHEMY_DATABASE_URI'] = connection_str


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
