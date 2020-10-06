# ChallengeBackend

Your goal is to create an app using the [spotify web api](https://developer.spotify.com/documentation/web-api/). You can make for example a [Flask](https://flask.palletsprojects.com/en/1.1.x/) or [Django rest framework](https://www.django-rest-framework.org/) project, it has to be able to authenticate to Spotify to fetch the new releases. Your job is to add two new features:
- A way to fetch data from spotify’s new releases API (/v1/browse/new-releases) and persist in a Postgresql DB (mandatory)
- A route : `/api/artists/` returning a JSON containing informations about artists that have released new tracks recently, from your local copy of today’s spotify’s new releases.

## Project Structure
The spotify auth is provided by us: (follows spotify web api.): it is located in `spotify_auth.py`.
The flow ends with a call to `/auth/callback/` which will give you the necessary access tokens.
To use it, we will provide you with the necessary: CLIENT_ID and CLIENT_SECRET.
Feel free to move it and re-organise as you please, we expect a well organised and clean code.
  
  
## Tech Specifications
- Be smart in your token usage (no unnecessary refreshes)
- Don’t request spotify artists at each request we send you
- The way you store the artists in Postgresql DB is going to be important use an ORM.
- As stated above, to test your server we will `GET /api/artists/` and we expect a nicely organised payload of artists. Make sure to use proper serialization and handle http errors. 

All stability, performance, efficiency adds-up are highly recommended.


## Choices made
- I went with Flask because it's the framework I know the most about
- To initiliaze the app, you need to set up a database in postgresql (I used v12) and modify the username, password and name of the database in `SETUP.py` as well as the client secret.
- The requirements for the python packages are in the standard requirements.txt file. In terminal, cd to the app folder and run `pip install -r requirements.txt`
- Still cd in the app folder, run 'python manage.py db init', then 'python manage.py db migrate' and finally 'python manage.py db upgrade'. You only need to do these steps for the first use of the app.


- I modified some of the functions provided for the authentification flow, while maintaining a copy of spotify.auth.py for reference
- On the first visit of http://localhost:5000/, the app will prompt you to accept to link your Spotify account. Once done, it will automatically retrieve the new releases from /v1/browse/new-releases and fetch the information on the artists (stored in a table). Once loaded, the page will show you a link to the json, accesible both by http://localhost:5000/api/artists/ and the `GET` request
- If you got your first token, your token should refresh automatically (if needed) if you visit http://localhost:5000/. Visiting the homepage should update the new release table and the artists table as well (it will do it once per day only). 
- I chose a few key information to retrieve from each artists : their name, up to three genres for their music, their Spotify popularity and the number of followers. I still put the artists id and href at the end. 
