import base64, json, requests, os, datetime
from SETUP import CLIENT_CREDENTIALS
#Declare Client_ID and client_SECRET as environnement variable



class SpotifyAuth(object):
    SPOTIFY_URL_AUTH = "https://accounts.spotify.com/authorize/"
    SPOTIFY_URL_TOKEN = "https://accounts.spotify.com/api/token/"
    RESPONSE_TYPE = "code"
    HEADER = "application/x-www-form-urlencoded"
    CLIENT_ID = CLIENT_CREDENTIALS['client_id']
    CLIENT_SECRET = CLIENT_CREDENTIALS['client_secret']
    CALLBACK_URL = "http://localhost:5000/auth"
    SCOPE = "user-read-email user-read-private"


    def getAuth(self, client_id, redirect_uri, scope):
        #Return the formatted url for the authentication process
        return (
            f"{self.SPOTIFY_URL_AUTH}"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            "&response_type=code"
        )

    def getToken(self, code, client_id, client_secret, redirect_uri):
        #Post the request to spotify API and get back the Token if no error
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        encoded = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            "Content-Type": self.HEADER,
            "Authorization": f"Basic {encoded}",
        }

        post = requests.post(self.SPOTIFY_URL_TOKEN, params=body, headers=headers)
        return self.handleToken(json.loads(post.text))

    def handleToken(self, response):
        #Catch an eventual error in the Token data and else get the basic information of the token
        if "error" in response:
            return response
        else:
            if "refresh_token" in response:
                return {
                    key: response[key]
                    for key in ["access_token", "expires_in", "refresh_token"]
                }
            else:
                return {
                    key: response[key]
                    for key in ["access_token", "expires_in"]
                }
    def refreshAuth(self, refresh_token):
        #Refresh a token if expired
        body = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        encoded = base64.b64encode(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode()).decode()
        headers = {
            "Content-Type": self.HEADER,
            "Authorization": f"Basic {encoded}"
        }
        post_refresh = requests.post(
            self.SPOTIFY_URL_TOKEN, params=body, headers=headers
        )

        return self.handleToken(json.loads(post_refresh.text))
    def getUser(self):
        return self.getAuth(
            self.CLIENT_ID, f"{self.CALLBACK_URL}/callback", self.SCOPE,
        )

    def getUserToken(self, code):
        return self.getToken(
            code, self.CLIENT_ID, self.CLIENT_SECRET, f"{self.CALLBACK_URL}/callback")