from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import asyncio
from aiohttp import web
import os
import json
import time


if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    spotify = Spotify()
    """
    params = {
        "seed_tracks": "6VCq9JcEi9EbEKl8XIdCgk,7Fur0xdBxvYbIT3qNUtYT2",
        "min_energy": "0.75",
        "market": "US",
        "limit": "25"
    }
    """

    if spotify.userAuth(conf, 'localhost', 8080, 'http://localhost:8080/', 'playlist-modify-public user-library-read'):
         data = spotify.get_all_users_saved_tracks()

    tracks_features = list()
    for i in data:
        i = i.split(':')[2]
        time.sleep(0.5)
        try:
            json = spotify.audio_features(i).json()
            if 'error' not in json.keys():
                features_json = dict()
                features_json['energy'] = json["energy"]
                features_json['loud'] = json["loudness"]
                features_json["dance"] = json["danceability"]
                features_json["speech"] = json["speechiness"]
                features_json["uri"] = json["uri"]
                tracks_features.append(features_json)
                print(i + ' checked')
            else:
                print(json['error'])
                break
        except Exception as e:
            print(e)

    light_tracks = list()

    for i in tracks_features:
        if i['energy'] <= 0.3 and i['loud'] >= -20.0 and i['dance'] <= 0.65 and i['speech'] <= 0.33:
            print(i['uri'])
            light_tracks.append(i['uri'])


    spotify.create_playlist("fgt0pmkaco3f1a5259n0ayqsa", "Test new", light_tracks)
