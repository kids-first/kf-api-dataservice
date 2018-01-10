import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    HOST = "0.0.0.0"
    SSL_DISABLE = os.environ.get("SSL_DISABLE", False)

    RESTPLUS_MASK_SWAGGER = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SSL_DISABLE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
            "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    SERVER_NAME = "localhost"
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
            "sqlite:///" + os.path.join(basedir, "data-test.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    # Should use postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            "sqlite:///" + os.path.join(basedir, "data.sqlite")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None


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
