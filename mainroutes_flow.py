from flask import Flask, Blueprint, render_template, request, jsonify, redirect, json
from Flask_framework import db
from models import NewRelease, UserCred, ArtistsInfo
from Auth import SpotifyAuth
import requests
from datetime import *


#from Groover
Authent=SpotifyAuth()


#Blueprint definition
routes = Blueprint('routes', __name__)



#Load the first line of the two databases to determine if empty or not




@routes.route('/')
def homePage():

    firstUser=UserCred.query.first()
    firstTrack=NewRelease.query.first()


    #initialize the table for the credentials only if it is empty as well as the first track
    #and the list of ID

    #set access_token as none and expires_at at yesterday so that the comparisons later work
    if firstUser is None:
        dummyUser=UserCred("None", "None", datetime.now(),date.today()-timedelta(1))
        db.session.add(dummyUser)
        db.session.commit()

    #Set the date of the last update as yesterday so that the comparisons later work
    if firstTrack is None:
        dummyTrack=NewRelease("dummy","dummy","dummy artists", "dummy id",date.today()-timedelta(1))
        db.session.add(dummyTrack)
        db.session.commit()

    firstUser=UserCred.query.first()
    firstArtists=ArtistsInfo.query.first()
    #Check if token is none, if yes button to log in to spotify
    if firstUser.access_token == "None" :
        return redirect('http://localhost:5000/auth')
    #If there is a token but it is expired, goes to /refresh to get a new one
    elif firstUser.expires_at <= datetime.now():
       return redirect("http://localhost:5000/refresh")
    #There is a token, but checks for the last update of the NewRelease table
    else:
        if firstUser.last_update < date.today():
            return redirect("http://localhost:5000/retrieval")
        elif firstArtists is None and firstUser.last_update == date.today():
            return redirect("http://localhost:5000/api/artists_retrieval")
        else: 
            return render_template("homepage_updated.html")   
    
@routes.route('/auth')
def Auth():
    return redirect(Authent.getUser())

#Get back the token if token is None, if not goes bak to homepage

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
        #Put the new user credentials in the table and goes back to homepage
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
        return redirect("http://localhost:5000/")
    
    #If the user goes to this page but has a token, does nothing
    #so that there is no unneeded query to the spotify API
    else:
        return redirect("http://localhost:5000")
    

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
    db.session.commit()
    return redirect("http://localhost:5000")



#Fetches the new releases and put them in the correct table, only accessible if a valid token 
#is in the UserCred table
@routes.route('/retrieval')
def retrieveNewRelease():
    firstUser=UserCred.query.first()
    #Check that the access token exists and is valid, if not for some reason
    #renders error.html
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
        return redirect("http://localhost:5000/refresh")

        

#Gets the ID of the artists from the NewRelease table, sends for the json of info

@routes.route("/api/artists_retrieval")
def GetArtistsInfo():
    #clear the artists table, loads up the credentials
    ArtistsInfo.query.delete()
    firstUser=UserCred.query.first()



    #Retrieve all of the artists ID, putting them on a list, creates the correct url to post
    Tracks=NewRelease.query.all()
    jsonAllTracks = jsonify([e.serialize() for e in Tracks]).get_json()
    list_of_id = []
    for item in jsonAllTracks:
        list_of_id.append(item['artists_identifier'])
    endpoint = "https://api.spotify.com/v1/artists"
    url_id = ",".join([item for item in list_of_id])
    
    lookup_url = endpoint+"?ids="+url_id


    #Checks for an existing and not expired user token
    if firstUser.access_token != 'None' and datetime.now() < firstUser.expires_at:
        headers = {
            "Authorization": "Bearer {}".format(firstUser.access_token)
        }
        try:
            json_of_artists = requests.get(lookup_url, headers=headers).json()
        except requests.exceptions.RequestException as e:
            return "Somehting went wrong while fetching the artists information:" +str(e)


        for artist in json_of_artists['artists']:

            #For now, 3 genres at a maximum are stored but easily expendable
            #Completes the array provided by spotify, slices it back to 3 items
            #and unpacks it to the correct variable

            genre_completed = artist['genres'] + ["None"]*(3-len(artist['genres']))
            genre_completed = genre_completed[0:3]
            genre1, genre2, genre3 = (genre_completed[i] for i in range(3))

            #Create the new entry in the artists table and adds it, commit at the end 
            #of the for loop
            entry = ArtistsInfo(
                name= artist['name'],
                genre1 = genre1,
                genre2 = genre2,
                genre3 = genre3,
                href = artist['href'],
                popularity = artist['popularity'],
                followers = artist['followers']['total'],
                artists_identifier = artist['id']
            )
            db.session.add(entry)
        db.session.commit()
            
    return redirect("http://localhost:5000")

#return a json if GET

@routes.route("/api/artists")
def getJson():
    ArtistsfromDB = ArtistsInfo.query.all()
    try:
        jsonAllArtists = jsonify([e.serialize() for e in ArtistsfromDB])
        return jsonAllArtists
    except requests.exceptions.RequestException as e:
        return "Somehting went wrong while fetching the new releases :" +str(e)

