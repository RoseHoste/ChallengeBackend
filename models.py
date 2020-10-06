from Flask_framework import db
import datetime
 
#Class for the NewRelease table

class NewRelease(db.Model):
    __tablename__ = "NewReleases"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable = False)
    album_type = db.Column(db.String(10))
    artists = db.Column(db.String(200))
    artists_identifier = db.Column(db.String(60))
    release_date = db.Column(db.Date)
    def __init__(self, name, album_type, artists,artists_identifier, release_date):
        self.name = name
        self.album_type = album_type
        self.artists = artists
        self.artists_identifier = artists_identifier
        self.release_date = release_date

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'album_type': self.album_type,
            'artists' : self.artists,
            'artists_identifier': self.artists_identifier,
            'release_date': self.release_date
        }


#Class for the users credentials table

class UserCred(db.Model):
    __tablename__ = 'Credentials'
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(200))
    refresh_token = db.Column(db.String(200))
    expires_at = db.Column(db.DateTime)
    last_update = db.Column(db.Date)

    def __init__(self, access_token, refresh_token, expires_at, last_update):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at= expires_at
        self.last_update = last_update

    def __repr__(self):
        return '<id {}>'.format(self.id)
        
#Class for the artists information table

class ArtistsInfo(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    genre1 = db.Column(db.String(100))
    genre2 = db.Column(db.String(100))
    genre3 = db.Column(db.String(100))
    href = db.Column(db.String(100))
    popularity = db.Column(db.Integer)
    followers = db.Column(db.Integer)
    artists_identifier = db.Column(db.String(60))

    def __init__(self, name, genre1, genre2, genre3, href, popularity, followers,
    artists_identifier
    
    ):
        self.name = name
        self.genre1 = genre1
        self.genre2 = genre2
        self.genre3 = genre3
        self.href = href
        self.popularity = popularity
        self.followers = followers
        self.artists_identifier = artists_identifier

    def serialize(self):
        return {
            'id': self.id, 
            'name': self.name,
            'genre': [genre for genre in [self.genre1, self.genre2, self.genre3] if genre!= 'None'],
            'href' : self.href,
            'popularity': self.popularity,
            'followers': self.followers,
            'artists_identifier': self.artists_identifier 
        }

    def __repr__(self):
        return '<id {}>'.format(self.id)


