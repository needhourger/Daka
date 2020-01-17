from config import config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

db=SQLAlchemy()
bootstrap=Bootstrap()
login_manager=LoginManager()

def create_app(config_name="default"):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app,db)

    from .main import main
    app.register_blueprint(main,url_prefix="/main")

    from .auth import auth
    app.register_blueprint(auth,url_prefix="/auth")

    return app
