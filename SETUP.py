#Replace username, password and database name with the appropriate strings
POSTGRES ={
    'user': <username>,
    'pw': <password>,
    'db': <database name>,
    'host': 'localhost',
    'port': '5432'

}
#Replace <client_secret> with your client secret provided by spotify, as a string
CLIENT_CREDENTIALS = {
    'client_id':'e18d6952d6854b6c9ab1a161a013e6e3',
    'client_secret': <client secret>
}

#Change the limit of new releases fetched, min is 1, max is 50, default is 20
limit=20