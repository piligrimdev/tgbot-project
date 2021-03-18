from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import json
import time

def Jaccard(setA, setB) -> float:
    if len(setA) != 0 and len(setB) != 0:

        return len(setA.intersection(setB)) / len(setA.union(setB))

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
                elif setSim >= 0.09:
                    lightSim.append(uniqeArtists[j])

        g1 = spotify.get_artist_genre(id1)
        for z in lightSim:
            item = z.split(":")[2]
            g2 = spotify.get_artist_genre(item)
            setg1 = set(g1)
            setg2 = set(g2)
            if Jaccard(setg1, setg2) >= 0.124:
                uniqeArtists[uniqeArtists.index(z)] = ""
                sim.append(z)

        listSim.append(sim)
    print("primary by artists suggestion selection")
    for i in listSim:
        for j in i:
            if j != i[0]:
                print("     " + j)
            else:
                print(j)


if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    spotify = Spotify()

    if spotify.userAuth(conf, 'localhost', 8080, 'http://localhost:8080/', ''):
        data, artists = spotify.get_playlist_tracks("07MHhkAywVS02QaojHnPOV", True)

    listOfSimilars(artists)
    """
    id1 = artists[0]
    id2 = artists[1]

    id1 = id1.split(":")[2]
    id2 = id2.split(":")[2]

    related1 = spotify.related_artists(id1)
    related2 = spotify.related_artists(id2)

    l1 = []
    g1 = spotify.get_artist_genre(id1)
    g2 = spotify.get_artist_genre(id2)

    for i in related1:
        l1.append(i['artist'])

    l2 = []

    for i in related2:
        l2.append(i['artist'])

    set1 = set(l1)
    set2 = set(l2)

    setg1 = set(g1)
    setg2 = set(g2)



    print(Jaccard(set1, set2))
    print(g1, " ", g2)
    print(Jaccard(setg1, setg2))
    """

