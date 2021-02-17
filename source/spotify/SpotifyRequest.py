import json
import requests
import asyncio
import base64
import webbrowser
from urllib import parse

from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.code = parseUrlParams(self.path)['code']


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
    def __init__(self, conf, auth=False, uri=None):
        self.session = requests.Session()
        self.url = 'https://api.spotify.com/v1/'
        self.code = ""
        if not auth:
            data = self.session.post('https://accounts.spotify.com/api/token', {'grant_type': 'client_credentials',
                                                                            'scopes': 'playlist-modify-public',
                                                                            'client_id': conf['CLIENT_ID'],
                                                                            'client_secret': conf[
                                                                                'CLIENT_SECRET']}).json()
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=data['access_token']),
                "Accept": "application/json",
                "Content-Type": "application/json"
                }
        else:
            self.id = conf["CLIENT_ID"]
            self.uri = uri
            data = self.session.get("https://accounts.spotify.com/authorize?client_id={}&response_type=code&redirect_uri={}&scope={}".format(self.id, uri, "playlist-modify-public"))
            if data.ok:

                webUrl = data.url

                server = HTTPServer(("localhost",8080), RequestHandler)
                server.code = None
                webbrowser.open(webUrl)
                server.handle_request()
                s = "{}:{}".format(conf['CLIENT_ID'], conf['CLIENT_SECRET'])
                utf = s.encode("utf-8")
                byt = base64.b64encode(utf).decode('utf-8')
                data = self.session.post('https://accounts.spotify.com/api/token',
                                         data={
                                             "grant_type": "authorization_code",
                                             "code": server.code,
                                             "redirect_uri": self.uri
                                         },
                                         headers={
                'Authorization': 'Basic {}'.format(byt),
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
                }

                )
                dataJson = data.json()
                if data.ok:
                    self.refresh_token = dataJson['refresh_token']
                    self.headers = {
                        'Authorization': 'Bearer {token}'.format(token=dataJson['access_token']),
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }



    def audio_features(self, id):
        return self.session.get(self.url + "audio-features/{0}".format(id), headers=self.headers)


    def similar_artist(self, parms):

        params_str = "?"

        for key, value in parms.items():
            params_str += key + "=" + value + "&"
        params_str = params_str[:-1]

        if params_str.find("seed_artist") != -1 or params_str.find("seed_genres") != -1 or params_str.find(
                "seed_tracks") != -1:
            return self.session.get(self.url + "recommendations/" + params_str,
                                    headers=self.headers)
        else:
            print("Seed artists, genres, or tracks required")
            return None

    def create_playlist(self, id, name, tracks=[], public=True, decription=None):
        body = {
            "name": name,
            "public": str(public)
        }
        if decription is not None:
            body["description"] = decription
        uris = str()
        for i in tracks:
            uris += i + "%2C"
        uris = uris[:-1]
        uris = uris.replace(":", "%3A")
        response = self.session.post(self.url + "users/" + id + '/playlists', json=body, headers=self.headers)
        playlistId = response.json()['id']
        response1 = self.session.post(self.url + "playlists/" + playlistId + '/tracks?',json={"uris": tracks, 'position': '0'}, headers=self.headers)
        print(response1)