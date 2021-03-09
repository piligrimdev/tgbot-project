from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import asyncio
from aiohttp import web
import os
import json
import time
import random
import operator

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
    """
    if spotify.userAuth(conf, 'localhost', 8080, 'http://localhost:8080/', 'playlist-modify-public'):
        data, artists = spotify.get_playlist_tracks("3bSjIwakzyBHIljtQhmHs7", True)

    tracks_features = list()

    artists_count = dict(sorted(artists.items(), key=operator.itemgetter(1), reverse=True))

    seed_artists = str()
    iter = 0
    for j in artists_count.keys():
        if iter > 4:
            break
        item = j
        item = item.split(':')[2]
        seed_artists += item + ","
        iter += 1
    seed_artists = seed_artists[:-1]

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

    count = len(data)
    sum_features = {
        "energy": 0,
        'loud': 0,
        "dance": 0,
        "speech": 0
    }
    for i in tracks_features:
        for key in i.keys():
            if key == "uri":
                continue
            sum_features[key] += i[key]

    aver_features = {
        "energy": 0,
        'loud': 0,
        "dance": 0,
        "speech": 0
    }
    for key in sum_features.keys():
        aver_features[key] = sum_features[key] / count

    seed_tracks = str()
    for i in range(5):
        randIndex = random.randint(0, count)
        item = data[randIndex]
        item = item.split(':')[2]
        seed_tracks += item + ","
    seed_tracks = seed_tracks[:-1]

    params = {
        "seed_tracks": seed_tracks,
        "seed_artist": seed_artists,
        "target_danceability": aver_features['dance'],
        "target_energy":  aver_features['energy'],
        "target_loudness":  aver_features['loud'],
        "target_speechiness":  aver_features['speech'],
        "limit": "35",
        "market": "US"
    }

    rec_data = spotify.similar_artist(params)

    uris = listOfTracks(rec_data.json())

    play_data = spotify.create_playlist("fgt0pmkaco3f1a5259n0ayqsa", "Super test", uris)


    print(play_data)

