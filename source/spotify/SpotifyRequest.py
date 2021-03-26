import json
import requests
import asyncio
import time
import base64
import webbrowser
from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.code = parseUrlParams(self.path)['code']

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        self.wfile.write("""<html>
        <head>
        <title>Spotify Authorization</title>
        </head>
        <body>
        This window can be closed.
        </body>
        </html>""".encode("utf-8"))


def listOfTracks(data):
    uris = list()
    ind = 0
    tracks = data['tracks']

    name, link = str(), str()
    for i in tracks:
        artists = str()
        name = i["name"]
        for j in i["artists"]:
            artists += j['name'] + ", "
        artists = artists[:-2]
        link = i["external_urls"]['spotify']
        uris.append(i["uri"])
        ind += 1
        print(name + " By " + artists + ": " + link)
    return uris

def parseUrlParams(url):
    return dict(parse.parse_qsl(parse.urlsplit(url).query))

class Spotify:
    def __init__(self, time):
        self.time = time
        self.session = requests.Session()
        self.apiUrl = 'https://api.spotify.com/v1/'
        self.headers = {
            'Authorization': 'Bearer {}',
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.authToken, self.refreshToken = None, None
        self.expiresIn = None

    def clientAuth(self, conf):

        s = "{}:{}".format(conf['CLIENT_ID'], conf['CLIENT_SECRET'])
        utf = s.encode("utf-8")
        byt = base64.b64encode(utf).decode('utf-8')

        headers = self.headers
        headers['Authorization'] = 'Basic {}'.format(byt)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        payload = {
            'grant_type': 'client_credentials',
            'client_id': conf['CLIENT_ID'],
            'client_secret': conf['CLIENT_SECRET']
        }

        data = self.session.post('https://accounts.spotify.com/api/token',
                                 data=payload,
                                 headers=headers
                                 )

        if data.ok:
            self.authToken = data.json()['access_token']
            self.expiresIn = data.json()['expires_in']
            self.headers['Authorization'] = 'Bearer {token}'.format(token=self.authToken)
            return True
        else:
            print(data.text['error'] + ': ' + data.text['error_description'])
            return False

    def userAuth(self, conf, host, port, redirect, scope):
        payload = {
                'client_id': conf['CLIENT_ID'],
                'response_type': 'code',
                'redirect_uri': redirect,
                'scope': scope
            }

        data = self.session.get("https://accounts.spotify.com/authorize", params=payload)

        if data.ok:
            server = HTTPServer((host, port), RequestHandler)
            server.code = None

            webbrowser.open(data.url)

            server.handle_request()

            s = "{}:{}".format(conf['CLIENT_ID'], conf['CLIENT_SECRET'])
            utf = s.encode("utf-8")
            byt = base64.b64encode(utf).decode('utf-8')

            payload = {
                    "grant_type": "authorization_code",
                    "code": server.code,
                    "redirect_uri": redirect
                }

            headers = self.headers
            headers['Authorization'] = 'Basic {}'.format(byt)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

            data = self.session.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)


            if data.ok:
                self.refreshToken = data.json()['refresh_token']
                self.authToken = data.json()['access_token']
                self.headers['Authorization'] = 'Bearer {token}'.format(token=self.authToken)
                return True
            else:
                error = json.loads(data.text)
                print(error['error'] + ': ' + error['error_description'])
                return False



    def audio_features(self, id):
        time.sleep(self.time)
        return self.session.get(self.apiUrl + "audio-features/{0}".format(id), headers=self.headers)

    def get_user_info(self):
        data = self.session.get(self.apiUrl + "me", headers=self.headers)
        js = data.json()
        if data.ok:
            return js
        else:
            print(js['error'])
            return dict()

    def get_all_users_saved_tracks(self):

        payload = {
            "offset": "0",
            "limit": "50"
        }

        nextStr = self.apiUrl + "me/tracks"
        track_list = list()
        while True:
            data = self.session.get(nextStr, params=payload, headers=self.headers)
            if data.ok:
                json = data.json()
                for i in json['items']:
                    track_list.append(i['track']["uri"])
                if json['next'] is not None:
                    nextStr = json['next']
                else:
                    return track_list
            else:
                return

    def get_playlist_tracks(self, playlist_id):
        payload = {
            "fields": "limit,next,items(track(name,uri,artists(uri)))",
            "offset": 0,
            "limit:": 100
        }
        nextStr = self.apiUrl + "playlists/" + playlist_id + "/tracks"
        track_list = list()
        while True:
            data = self.session.get(nextStr, params=payload,  headers=self.headers)
            if data.ok:
                json = data.json()
                for i in json['items']:
                    track_list.append({'track': i['track']["uri"], 'artist': i['track']['artists'][0]["uri"]})
                    #artists_list.append(i['track']['artists'][0]["uri"])
                if json['next'] is not None:
                    nextStr = json['next']
                else:
                    return track_list
            else:
                print("ERROR")
                return

    def track_recommendation(self, parms):
        if "seed_artist" in parms.keys() or \
            "seed_genres" in parms.keys() or \
                "seed_tracks" in parms.keys():
                    data = self.session.get(self.apiUrl + "recommendations", params=parms, headers=self.headers)
                    js = data.json()
                    if data.ok:
                        return js
                    else:
                        print(js['error'])
                        return dict()
        else:
            print("Seed artists, genres, or tracks required")
            return None

    def related_artists(self, id):
        time.sleep(self.time)
        data = self.session.get(self.apiUrl + "artists/{}/related-artists".format(id), headers=self.headers)
        artists_list = []

        if data.ok:
            dataJson = data.json()
            for i in dataJson['artists']:
                item = dict()
                item['artist'] = i['id']
                item['genres'] = i['genres']
                artists_list.append(item)
            return artists_list
        else:
            print(data)
            return []

    def get_artist_genre(self, id):
        time.sleep(self.time)
        data = self.session.get(self.apiUrl + "artists/{}".format(id), headers=self.headers)

        if data.ok:
            js = data.json()
            return js['genres']
        else:
            print(data)
            return []

    def get_artist_name(self, id):
        time.sleep(self.time)
        data = self.session.get(self.apiUrl + "artists/{}".format(id), headers=self.headers)

        js = data.json()
        if data.ok:
            return js['name']
        else:
            print(js['error'])
            return ""

    def create_playlist(self, id, name, tracks=[], public=True, decription=None):
        body = {
            "name": name,
            "public": str(public)
        }
        if decription is not None:
            body["description"] = decription


        response = self.session.post(self.apiUrl + "users/" + id + '/playlists', json=body, headers=self.headers)
        playlistId = response.json()['id']

        uris = list()
        counter = 0
        for i in tracks:
            if counter != 100:
                uris.append(i)
                counter += 1
            else:
                response1 = self.session.post(self.apiUrl + "playlists/" + playlistId + '/tracks',json={"uris": uris, 'position': '0'}, headers=self.headers)

                if not response1.ok:
                    error = json.loads(response1.text)
                    print(error['error'] + ': ' + error['error_description'])
                    return

                uris = list()
                counter = 0

        if len(uris) != 0:
            response1 = self.session.post(self.apiUrl + "playlists/" + playlistId + '/tracks',
                                          json={"uris": uris, 'position': '0'}, headers=self.headers)

            if not response1.ok:
                error = json.loads(response1.text)
                print(error['error'] + ': ' + error['error_description'])
