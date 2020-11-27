# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json

import spotipy
import sqlite3 , requests

CLIENT_ID = '1bc8d28430a54a489afccd025e285f61'
CLIENT_SECRET = '6963aaeddb1848eab5de861e4a836143'

conn = sqlite3.connect('users.sqlite')
cur = conn.cursor()

#cur.execute('CREATE TABLE V(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT)')
#cur.execute('INSERT INTO V(name, email) VALUES(?, ?)', ('homer', 'homer@simpson.com'))
#conn.commit()
#cur.close()

def create_tables():
    cur.execute('CREATE TABLE IF NOT EXISTS Artists(id TEXT PRIMARY KEY , name TEXT, followers INTEGER,popularity INTEGER )')
    cur.execute('CREATE TABLE IF NOT EXISTS Albums(id TEXT PRIMARY KEY , name TEXT, release_date TEXT)')
    cur.execute('create table IF NOT EXISTS Artists_Albums(artistId text constraint Artists_Albums___fk references Artists (id),albumId TEXT constraint Artists_Albums___fk_2 references Albums (id))')
    cur.execute('CREATE TABLE IF NOT EXISTS Tracks(id TEXT PRIMARY KEY , name TEXT, albumid TEXT references Albums(id),duration_ms INTEGER )')
    cur.execute('CREATE TABLE IF NOT EXISTS Artists_Tracks(artistId TEXT references Artists(artistId), trackId TEXT references Tracks(id))')
    conn.commit()



def table_populating():
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })


    access_token = auth_response.json()['access_token']

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    params = {
        'ids':'3m49WVMU4zCkaVEKb8kFW7,1mYsTxnqsietFxj1OgoGbG' # I have picked two artistsid
    }
    BASE_URL = 'https://api.spotify.com/v1/'

    # Get Artists Info
    t = requests.get(BASE_URL +'artists', headers=headers,params=params)

    artists=t.json()['artists']

    table_rows=[(i["id"],i["name"],i["followers"]["total"],i["popularity"]) for i in artists]
    sql_statement = 'INSERT INTO Artists VALUES (?, ?, ?, ?)'

    cur.executemany(sql_statement, table_rows)

    for i in artists:
        r = requests.get(BASE_URL + 'artists/' + i["id"] + '/albums',headers=headers,params={'include_groups': 'album', 'limit': 20})
        albums=r.json()['items']
        table_rows = [(j["id"], j["name"], j["release_date"]) for j in albums]
        sql_statement = 'INSERT INTO Albums VALUES (?, ?, ?)'
        cur.executemany(sql_statement, table_rows)

        table_rows = [(i["id"], j["id"]) for j in albums]
        sql_statement = 'INSERT INTO Artists_Albums VALUES (?, ?)'
        cur.executemany(sql_statement, table_rows)

        for j in albums:
            s = requests.get(BASE_URL + 'albums/' + j["id"] + '/tracks', headers=headers)
            tracks = s.json()['items']

            table_rows = [(s["id"], s["name"], j["id"],s["duration_ms"]) for s in tracks]
            sql_statement = 'INSERT INTO Tracks VALUES (?, ?, ?,?)'
            cur.executemany(sql_statement, table_rows)

            table_rows = [(i["id"], s["id"]) for s in tracks]
            sql_statement = 'INSERT INTO Artists_Tracks VALUES (?, ?)'
            cur.executemany(sql_statement, table_rows)


    conn.commit()
    cur.close()

    # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_tables()
    table_populating()


