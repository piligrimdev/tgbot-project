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
    def __init__(self):
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
                                 ).json()
        if data.ok:
            self.authToken = data['access_token']
            self.expiresIn = data['expires_in']
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

            strPayload = '?client_id={}&response_type=code&redirect_uri={}&scope={}'.format(conf['CLIENT_ID'], redirect, scope)
            data = self.session.get("https://accounts.spotify.com/authorize" + strPayload)

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
        return self.session.get(self.apiUrl + "audio-features/{0}".format(id), headers=self.headers)


    def similar_artist(self, parms):

        params_str = "?"

        for key, value in parms.items():
            params_str += key + "=" + value + "&"
        params_str = params_str[:-1]

        if params_str.find("seed_artist") != -1 or params_str.find("seed_genres") != -1 or params_str.find(
                "seed_tracks") != -1:
            return self.session.get(self.apiUrl + "recommendations/" + params_str,
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
            uris += i + ","
        uris = uris[:-1]
        response = self.session.post(self.apiUrl + "users/" + id + '/playlists', json=body, headers=self.headers)
        playlistId = response.json()['id']
        response1 = self.session.post(self.apiUrl + "playlists/" + playlistId + '/tracks?',json={"uris": tracks, 'position': '0'}, headers=self.headers)
        print(response1)