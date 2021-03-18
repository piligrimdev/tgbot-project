from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import json
import time


if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    spotify = Spotify()

    if spotify.userAuth(conf, 'localhost', 8080, 'http://localhost:8080/', 'playlist-modify-public'):
        data, artists = spotify.get_playlist_tracks("3bSjIwakzyBHIljtQhmHs7", True)

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
                features_json["valence"] = json["valence"]
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
        "speech": 0,
        "valence": 0
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
        "speech": 0,
        "valence": 0
    }
    for key in sum_features.keys():
        aver_features[key] = sum_features[key] / count

    seed_tracks = str()
    seed_artists = str()
    full_uris = list()
    counter = 0
    for i, j in zip(data, artists):
        if counter != 5:
            item = i.split(':')[2]
            seed_tracks += item + ","

            item1 = j.split(':')[2]
            seed_artists += item1 + ","
            counter += 1
        else:
            seed_tracks = seed_tracks[:-1]
            seed_artists = seed_artists[:-1]

            params = {
                "seed_tracks": seed_tracks,
                "seed_artist": seed_artists,
                "target_danceability": aver_features['dance'],
                "target_energy":  aver_features['energy'],
                "target_loudness":  aver_features['loud'],
                "target_speechiness":  aver_features['speech'],
                "target_valence": aver_features['valence'],
                "limit": "10",
                "market": "US"
            }

            rec_data = spotify.similar_artist(params)
            uris = listOfTracks(rec_data.json())
            full_uris.extend(list(set(uris).difference(set(full_uris))))

            counter = 0
            seed_tracks = str()
            seed_artists = str()


    play_data = spotify.create_playlist("fgt0pmkaco3f1a5259n0ayqsa", "Super test 6", full_uris)


    print(play_data)
