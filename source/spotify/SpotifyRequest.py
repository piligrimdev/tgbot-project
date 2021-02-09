import json
import requests
import asyncio
import aiohttp

class Spotify:
    def __init__(self, conf):
        self.session = requests.Session()
        self.url = 'https://api.spotify.com/v1/'
        data = self.session.post('https://accounts.spotify.com/api/token', {'grant_type': 'client_credentials',
                                'client_id': conf['CLIENT_ID'],
                                'client_secret': conf['CLIENT_SECRET']}).json()
        self.headers = {
            'Authorization': 'Bearer {token}'.format(token=data['access_token']),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def audio_features(self, id):
        return self.session.get(self.url + "audio-features/{0}".format(id), headers=self.headers)

    def similar_artist(self, parms):

            parms_str = "?"
            for key, value in parms.items():
                parms_str += key + "=" + value + "&"
            parms_str = parms_str[:-1]

            if parms_str.find("seed_artist") != -1 or parms_str.find("seed_genres") != -1 or parms_str.find("seed_tracks") != -1:
                return self.session.get(self.url + "recommendations/"+ parms_str,
                                        headers=self.headers)
            else:
                print("Seed artists, genres, or tracks required")
                return None