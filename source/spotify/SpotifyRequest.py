import json
import requests
import asyncio
import aiohttp

class Spotify:
    def __init__(self, conf):
        self.session = requests.Session()
        self.url = 'https://api.spotify.com/v1/'
        data = self.session.post(self.url, {'grant_type': 'client_credentials',
                                'client_id': conf['CLIENT_ID'],
                                'client_secret': conf['CLIENT_SECRET']}).json()
        self.headers = {
             'Authorization': 'Bearer {token}'.format(token=data['access_token'])
        }

    def audio_features(self, id):
        return self.session.get(self.url + "audio-features/{0}".format(id)).json
