from flask import Flask, Blueprint, render_template, request, jsonify, redirect, json
from Flask_framework import db
from models import NewRelease, UserCred, ArtistsInfo
from Auth import SpotifyAuth
import requests
from datetime import *
from PrepArtists import *
from SETUP import limit

base_local_url = "http://localhost:5000/"

#from Groover, slightly modified
Authent=SpotifyAuth()
#Blueprint definition
routes = Blueprint('routes', __name__)

@routes.route('/')
def homePage():
    # Query the first line of each database to check if empty
    firstUser=UserCred.query.first()
    #Check if token is none, if yes prompt to log in to spotify
    if firstUser is None :
        return redirect(base_local_url+"auth")
    #There is a token, but checks for the last update of the NewRelease table
    else:
        firstArtists=ArtistsInfo.query.first()
        #If the last update is before today
        if firstUser.last_update < date.today():
            #If the token is expired
            if firstUser.expires_at <= datetime.now():
                return redirect(base_local_url+"refresh")
            else:
                return redirect(base_local_url+"releases_retrieval")
        #Check if the artists information table is empty and if the new release database is up to date
        elif firstArtists is None and firstUser.last_update == date.today():
            return redirect(base_local_url+"api/artists_retrieval")
        #If the last update is today and the artist table is not empty
        else: 
            return render_template("homepage_updated.html")   


#Goes to the log in page from Spotify and if already logged in, goes back to auth/callback/{code}
@routes.route('/auth')
def Auth():
    return redirect(Authent.getUser())

#Get back the token if token is None, if not for some reason goes back to homepage

@routes.route('/auth/callback')
def AuthUserToken():
    code = request.args.get('code')
    #Loads the first user
    firstUser=UserCred.query.first()
    
    #If there is no token, gets one
    if firstUser.access_token == "None":
        #Delete dummyUser
        UserCred.query.filter_by(access_token="None").delete()
        #Use the provided function to get the token
        response = Authent.getUserToken(code)
        #Put the new user credentials in the table and goes back to "/"
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
            return response.status_code
        return redirect(base_local_url)
    
    #If the user goes to this page but has a token, does nothing
    #so that there is no unneeded query to the spotify API
    else:
        return redirect(base_local_url)
    

#Page to refresh an expired token
@routes.route("/refresh")
def RefreshToken():
    #Loads the first user, it has been checked that the refresh token exists back at the homepage
    firstUser=UserCred.query.first()

    #Use the provided function to refresh the token
    response = Authent.refreshAuth(firstUser.refresh_token)
    #Update the credentials and goes back to homepage
    firstUser.access_token = response['access_token']
    firstUser.expires_at = datetime.now()+timedelta(seconds=response['expires_in'])
    if "refresh_token" in response:
        firstUser.refresh_token=response['refresh_token']
    db.session.commit()
    return redirect(base_local_url)



#Fetches the new releases and put them in the correct table, only accessible if a valid token 
#is in the UserCred table

@routes.route('/releases_retrieval')
def retrieveNewRelease():
    firstUser=UserCred.query.first()
    #if there is no need to refresh the new release table, go back to homepage
    if firstUser.last_update == date.today():
        return redirect(base_local_url)

    #Check that the access token exists and is valid, if not for some reason
    #goes back to refresh to turn once more and get back here with a valid token
    
    if firstUser.access_token != 'None' and datetime.now() < firstUser.expires_at:

        #Post to spotify API to get the new release data, after having wiped down the table

        NewRelease.query.delete()
        headers = {
            "Authorization": "Bearer {}".format(firstUser.access_token)
            }
        endpoint = f"https://api.spotify.com/v1/browse/new-releases?limit={limit}"
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

            #Change the last update datapoint for the user
            firstUser.last_update = date.today()

            db.session.commit()

            #Wipes down the artists info table to prepare for its repopulation
            ArtistsInfo.query.delete()
            return redirect(base_local_url)
    else:
        return redirect(base_local_url+"refresh")

        

#Gets the ID of the artists from the NewRelease table, sends for the json of info

@routes.route("/api/artists_retrieval")
def GetArtistsInfo():
    #loads up the credentials  
    firstUser=UserCred.query.first()

    #Retrieve all of the artists ID, putting them on a list, creates the correct url to post
    lookup_url = GetArtistsUrl()


    #Checks for an existing and not expired user token
    if firstUser.access_token != 'None' and datetime.now() < firstUser.expires_at:
        headers = {
            "Authorization": "Bearer {}".format(firstUser.access_token)
        }
        try:
            json_of_artists = requests.get(lookup_url, headers=headers).json()
        except requests.exceptions.RequestException as e:
            return "Somehting went wrong while fetching the artists information:" +str(e)

        #Sends the data to the correct table and commits

        PopulateTable(json_of_artists)
        
        #Goes back to hompeage

        return redirect(base_local_url)
    else:
        return redirect(base_local_url+"refresh")

#return a json
#The GET method is built in Blueprint route so it is not explicitely declared

@routes.route("/api/artists")
def getJson():
    ArtistsfromDB = ArtistsInfo.query.all()
    try:
        jsonAllArtists = jsonify([e.serialize() for e in ArtistsfromDB])
        return jsonAllArtists
    except requests.exceptions.RequestException as e:
        return "Something went wrong while fetching the artists information:" +str(e)

