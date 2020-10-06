from flask import Flask
from Auth import SpotifyAuth
from flask_sqlalchemy import SQLAlchemy
from SETUP import POSTGRES
#Initialize the SQLAlchemy object with the credentials for the postgres connection
db=SQLAlchemy()

#Initiliaze the App with some configurations (utf-8 support, URI for database)
SpotifyApp = Flask(__name__, static_url_path="", static_folder="static")

SpotifyApp.config['JSON_AS_ASCII'] = False
SpotifyApp.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(SpotifyApp)

#Tell Flask where the routes are, initialize the db
with SpotifyApp.app_context():
    db.create_all()
    db.session.commit()
    from mainroutes_flow import routes
    SpotifyApp.register_blueprint(routes)
    SpotifyApp.config['DEBUG'] = False
