from flask import Flask, Blueprint, render_template, request, jsonify, redirect, json
from models import NewRelease, UserCred, ArtistsInfo
from Flask_framework import db
from Auth import SpotifyAuth
import requests
from datetime import *
from urllib.parse import urlencode

#from Groover
Authent=SpotifyAuth()

routes = Blueprint('routes', __name__)

firstUser=UserCred.query.first()
firstTrack=NewRelease.query.first()
#initialize the table for the credentials only if it is empty as well as the first track
#and the list of ID
if firstUser is None:
    dummyUser=UserCred("None", "None", datetime.now(),date.today()-timedelta(1))
    db.session.add(dummyUser)
    db.session.commit()
if firstTrack is None:
    dummyTrack=NewRelease("dummy","dummy","dummy artists", "dummy id",date.today()-timedelta(1))
    db.session.add(dummyTrack)
    db.session.commit()
#Homepage
@routes.route('/')
def homePage():
    firstUser=UserCred.query.first()
    if firstUser.access_token == "None" :
        return render_template("homepage.html")
    elif firstUser.expires_at <= datetime.now():
       return redirect("http://localhost:5000/refresh")
    else:
        if firstUser.last_update < date.today():
            return render_template("homepage_connected.html")
        else: 
            return render_template("homepage_updated.html")
    
    


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
    firstUser=UserCred.query.first()
    if firstUser.access_token == "None":
        #Delete dummyUser
        UserCred.query.filter_by(access_token="None").delete()
        response = Authent.getUserToken(code)
        try:
            User=UserCred(
                access_token = response['access_token'],
                expires_at = datetime.now()+timedelta(seconds=response['expires_in']),
                refresh_token = response['refresh_token'],
                last_update = date.today()-timedelta(1)
            )
            db.session.add(User)
            db.session.commit()
        except Exception as e:
            return(str(e))
        return redirect("http://localhost:5000/")
    else:
        return redirect("http://localhost:5000")
    


@routes.route("/refresh")
def RefreshToken():
    firstUser=UserCred.query.first()
    response = Authent.refreshAuth(firstUser.refresh_token)
    firstUser.access_token = response['access_token']
    firstUser.expires_at = datetime.now()+timedelta(seconds=response['expires_in'])
    db.session.commit()
    return redirect("http://localhost:5000")

@routes.route('/retrieval')
def retrieveNewRelease():
    firstUser=UserCred.query.first()
    #Check that the access token exists and is valid
    if firstUser.access_token != 'None' and datetime.now() < firstUser.expires_at:
        #Post to spotify API to get the new release data, after having wiped down the table
        NewRelease.query.delete()
        headers = {
            "Authorization": "Bearer {}".format(firstUser.access_token)
            }
        endpoint = "https://api.spotify.com/v1/browse/new-releases"
        request=requests.get(endpoint, headers=headers)
        
        
        #If error, stop and go to error.html
        
        
        
        if request.status_code not in range(200,299):
            return render_template('error.html')
        
        else:
            for album in request.json()['albums']['items']:
                entry = NewRelease(
                    name= album['name'],
                    album_type = album['album_type'],
                    artists = album['artists'][0]['name'],
                    artists_identifier = album['artists'][0]['id'],
                    release_date = date.fromisoformat(album['release_date'])
                )
                db.session.add(entry)

            firstUser.last_update = date.today()
            db.session.commit()
            return redirect("http://localhost:5000")
    else:
        return render_template("error.html")

        

@routes.route("/api/artists")
def GetArtistsInfo():
    firstUser=UserCred.query.first()
    #Retrieve all of the artists ID
    Tracks=NewRelease.query.all()
    jsonAllTracks = jsonify([e.serialize() for e in Tracks]).get_json()
    list_of_id = []
    for item in jsonAllTracks:
        list_of_id.append(item['artists_identifier'])
    endpoint = "https://api.spotify.com/v1/artists"
    url_id = ",".join([item for item in list_of_id])
    
    lookup_url = endpoint+"?ids="+url_id

    if firstUser.access_token != 'None' and datetime.now() < firstUser.expires_at:
        headers = {
            "Authorization": "Bearer {}".format(firstUser.access_token)
        }
        json_of_artists = requests.get(lookup_url, headers=headers).json()

    return json_of_artists



 