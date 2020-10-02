from flask import Flask, Blueprint, render_template, request, jsonify, redirect
from models import NewRelease
from Flask_framework import db
from Auth import SpotifyAuth

#from Groover
Authent=SpotifyAuth()

routes = Blueprint('routes', __name__)

#Homepage
@routes.route('/')
def homePage():
    return render_template("homepage.html")

#Add to the database with the correct query
@routes.route("/add")
def add_track():
    name=request.args.get('name')
    try:
        Track=NewRelease(
            name=name,
        )
        db.session.add(Track)
        db.session.commit()
        return "Track added. Track id={}".format(Track.id)
    except Exception as e:
	    return(str(e))
#List all the tracks to the database

@routes.route("/getalltracks")
def get_alltracks():
    try:
        Tracks=NewRelease.query.all()
        return jsonify([e.serialize() for e in Tracks])
    except Exception as e:
	    return(str(e))

#Starts the authentication process
@routes.route('/auth')
def Auth():
    
    return redirect(Authent.getUser())


#Get back the token
@routes.route('/auth/callback')
def AuthUserToken():
    code = request.args.get('code')
    response = Authent.getUserToken(code)
    return response