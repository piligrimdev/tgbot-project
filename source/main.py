from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import json
import time

def Jaccard(setA, setB) -> float:
    if len(setA) != 0 and len(setB) != 0:

        return len(setA.intersection(setB)) / len(setA.union(setB))
    else:
        return 0

def listOfSimilars(artists):
    uniqeArtists = list(set(artists))
    listSim = []
    for i in range(len(uniqeArtists)):
        if uniqeArtists[i] == "":
            continue
        if i + 1 > len(uniqeArtists):
            break
        sim = [uniqeArtists[i]]
        lightSim = []
        for j in range(i + 1, len(uniqeArtists)):
            if uniqeArtists[j] != "" and uniqeArtists[i] != "":
                id1, id2 = uniqeArtists[i], uniqeArtists[j]
                id1 = id1.split(":")[2]
                id2 = id2.split(":")[2]
                related1, related2 = spotify.related_artists(id1), spotify.related_artists(id2)
                l1 = []
                l2 = []
                for z in related1:
                    l1.append(z['artist'])
                for z in related2:
                        l2.append(z['artist'])
                setSim = Jaccard(set(l1), set(l2))
                if setSim >= 0.3:
                    sim.append(uniqeArtists[j])
                    uniqeArtists[j] = ""
                elif setSim > 0.09:
                    lightSim.append(uniqeArtists[j])

        g1 = spotify.get_artist_genre(id1)
        for z in lightSim:
            item = z.split(":")[2]
            g2 = spotify.get_artist_genre(item)
            setg1 = set(g1)
            setg2 = set(g2)
            if Jaccard(setg1, setg2) > 0.124:
                uniqeArtists[uniqeArtists.index(z)] = ""
                sim.append(z)

        listSim.append(sim)
    for i in listSim:
        for j in i:
            if j != i[0]:
                print("     " + j)
            else:
                print(j)
    return listSim


if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    spotify = Spotify()

    if spotify.userAuth(conf, 'localhost', 8080, 'http://localhost:8080/', 'playlist-modify-public'):
        data, artists = spotify.get_playlist_tracks("3bSjIwakzyBHIljtQhmHs7", True)

    similar_artists = listOfSimilars(artists)

    tracks_features = list()

    for i in data:
        i = i['track'].split(':')[2]
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

    full_uris = list()
    for artists in similar_artists:
        seed_tracks = str()
        seed_artists = str()
        tracks = []
        for track in data:
            if track['artist'] in artists:
                tracks.append(track)
        counter = 0
        for track in tracks:
            if counter != 5:
                item = track['track'].split(':')[2]
                seed_tracks += item + ','

                item1 = track['artist'].split(':')[2]
                seed_artists += item1 + ','

                counter += 1
            else:
                seed_tracks = seed_tracks[:-1]
                seed_artists = seed_artists[:-1]

                params = {
                    "seed_tracks": seed_tracks,
                    "seed_artist": seed_artists,
                    "target_danceability": aver_features['dance'],
                    "target_energy": aver_features['energy'],
                    "target_loudness": aver_features['loud'],
                    "target_speechiness": aver_features['speech'],
                    "target_valence": aver_features['valence'],
                    "limit": "5",
                    "market": "US"
                }

                rec_data = spotify.similar_artist(params)
                uris = listOfTracks(rec_data.json())
                full_uris.extend(list(set(uris).difference(set(full_uris))))

                counter = 0
                seed_tracks = str()
                seed_artists = str()
        if len(seed_tracks) != 0:
            seed_tracks = seed_tracks[:-1]
            seed_artists = seed_artists[:-1]

            params = {
                "seed_tracks": seed_tracks,
                "seed_artist": seed_artists,
                "target_danceability": aver_features['dance'],
                "target_energy": aver_features['energy'],
                "target_loudness": aver_features['loud'],
                "target_speechiness": aver_features['speech'],
                "target_valence": aver_features['valence'],
                "limit": "5",
                "market": "US"
            }
            names = ""
            for i in artists:
                id = i.split(':')[2]
                name = spotify.get_artist_name(id)
                names += name + " "
            print("\nTracks based on " + names + "\n")
            rec_data = spotify.similar_artist(params)
            uris = listOfTracks(rec_data.json())
            full_uris.extend(list(set(uris).difference(set(full_uris))))


    play_data = spotify.create_playlist("fgt0pmkaco3f1a5259n0ayqsa", "Super duper test 8", full_uris)


    print(play_data)