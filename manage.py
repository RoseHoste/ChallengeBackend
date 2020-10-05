from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from Flask_framework import AuthApp, db

migrate = Migrate(AuthApp, db, compare_type=True)
manager = Manager(AuthApp)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()