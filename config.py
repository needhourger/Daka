import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY=os.urandom(24)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+basedir+"/data.db"
    ADMIN_LIST=["admin"]
    DEBUG=True
    PORT=80

config={
    "default":DevConfig,
    "dev":DevConfig
}
