from flask import Flask
from Auth import SpotifyAuth
from flask_sqlalchemy import SQLAlchemy

#Initialize the SQLAlchemy object with the credentials for the postgres connection
db=SQLAlchemy()

POSTGRES ={
    'user':'groover',
    'pw':'groover',
    'db': 'challenge',
    'host': 'localhost',
    'port': '5432'

}
#Initiliaze the App with some configurations (utf-8 support, URI for database)
AuthApp = Flask(__name__, static_url_path="", static_folder="static")

AuthApp.config['JSON_AS_ASCII'] = False
AuthApp.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(AuthApp)

#Tell Flask where the routes are, initialize the db
with AuthApp.app_context():
    from mainroutes_flow import routes
    AuthApp.register_blueprint(routes)
    db.create_all()
    AuthApp.config['DEBUG'] = True
