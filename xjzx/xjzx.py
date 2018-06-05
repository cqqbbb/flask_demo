from flask_script import Manager
from app import create_app
from config import DevelopConfig
from models import db
from flask_migrate import MigrateCommand, Migrate
from super_command import CreateAdminCommand, RegisterUserCommand,LoginCountCommand

app = create_app(DevelopConfig)

manager = Manager(app)

db.init_app(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command('admin',CreateAdminCommand)
manager.add_command('register',RegisterUserCommand)
manager.add_command('login',LoginCountCommand)


if __name__ == '__main__':
    manager.run()
