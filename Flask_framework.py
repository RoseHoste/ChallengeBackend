from flask import Flask
from Auth import SpotifyAuth
from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()

POSTGRES ={
    'user':'groover',
    'pw':'groover',
    'db': 'challenge',
    'host': 'localhost',
    'port': '5432'

}

AuthApp = Flask(__name__, static_url_path="", static_folder="static")

AuthApp.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(AuthApp)


with AuthApp.app_context():
    from mainroutes import routes
    AuthApp.register_blueprint(routes)
    db.create_all()
    AuthApp.config['DEBUG'] = True


