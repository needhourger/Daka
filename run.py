from app import create_app,db
from app.models import User,Role,Record

from flask_script import Manager,Shell
from flask_migrate import MigrateCommand,Migrate
import os
basedir=os.path.abspath(os.path.dirname(__file__))

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Record=Record)

if __name__ == "__main__":
    app=create_app()
    manager=Manager(app)
    migrate=Migrate(app,db)
    manager.add_command("shell",Shell(make_context=make_shell_context))
    manager.add_command("db",MigrateCommand)

    manager.run()
