from flask import jsonify
from Flask_framework import db
from models import NewRelease, ArtistsInfo

def GetArtistsUrl():
    Tracks=NewRelease.query.all()
    jsonAllTracks = jsonify([e.serialize() for e in Tracks]).get_json()
    list_of_id = []
    for item in jsonAllTracks:
        list_of_id.append(item['artists_identifier'])
    endpoint = "https://api.spotify.com/v1/artists"
    url_id = ",".join([item for item in list_of_id])
    lookup_url = endpoint+"?ids="+url_id
    return lookup_url


def PopulateTable(response):

    for artist in response['artists']:

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