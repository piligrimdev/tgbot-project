import aiohttp
import asyncio
import json
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from source.spotify.SpotifyRequest import listOfTracks, parseUrlParams, Jaccard, RequestHandler


class SpotifyAsync:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.apiUrl = 'https://api.spotify.com/v1/'
        self.headers = {
            'Authorization': 'Bearer {}',
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.authToken, self.refreshToken = None, None
        self.expiresIn = None

    async def clientAuth(self, conf):

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

        data = await self.session.post('https://accounts.spotify.com/api/token',
                                       data=payload,
                                       headers=headers
                                       )

        if data.ok:
            self.authToken = (await data.json())['access_token']
            self.expiresIn = (await data.json())['expires_in']
            self.headers['Authorization'] = 'Bearer {token}'.format(token=self.authToken)
            return True
        else:
            print((await data.reason)['error'] + ': ' + (await data.reason)['error_description'])
            return False

    async def getAuthLink(self, conf, redirect, scope, state):
        payload = {
            'client_id': conf['CLIENT_ID'],
            'response_type': 'code',
            'redirect_uri': redirect,
            'scope': scope,
            'state': state
        }

        return (await self.session.get("https://accounts.spotify.com/authorize", params=payload)).url

    async def localUserAuth(self, conf, host, port, redirect):
        server = HTTPServer((host, port), RequestHandler)
        server.code = None

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

        data = await self.session.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)

        if data.ok:
            self.refreshToken = (await data.json())['refresh_token']
            self.authToken = (await data.json())['access_token']
            self.headers['Authorization'] = 'Bearer {token}'.format(token=self.authToken)
            return True
        else:
            error = json.loads(data.reason)
            print(error['error'] + ': ' + error['error_description'])
            return False

    async def userAuth(self, conf, redirect, code):

        s = "{}:{}".format(conf['CLIENT_ID'], conf['CLIENT_SECRET'])
        utf = s.encode("utf-8")
        byt = base64.b64encode(utf).decode('utf-8')

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect
        }

        headers = self.headers
        headers['Authorization'] = 'Basic {}'.format(byt)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        data = await self.session.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)

        if data.ok:
            self.refreshToken = (await data.json())['refresh_token']
            self.authToken = (await data.json())['access_token']
            self.headers['Authorization'] = 'Bearer {token}'.format(token=self.authToken)
            return True
        else:
            print((await data.reason)['error'] + ': ' + (await data.reason)['error_description'])
            return False

    async def audio_features(self, id):
        return await self.session.get(self.apiUrl + "audio-features/{0}".format(id), headers=self.headers)

    async def get_user_info(self):
        data = await self.session.get(self.apiUrl + "me", headers=self.headers)
        js = await data.json()
        if data.ok:
            return js
        else:
            print(js['error'])
            return dict()

    async def get_all_users_saved_tracks(self):

        payload = {
            "offset": "0",
            "limit": "50"
        }

        nextStr = self.apiUrl + "me/tracks"
        track_list = list()
        while True:
            data = await self.session.get(nextStr, params=payload, headers=self.headers)
            if data.ok:
                json = await data.json()
                for i in json['items']:
                    track_list.append(i['track']["uri"])
                if json['next'] is not None:
                    nextStr = json['next']
                else:
                    return track_list
            else:
                return

    async def get_playlist_tracks(self, playlist_id):
        payload = {
            "fields": "limit,next,items(track(name,uri,artists(uri)))",
            "offset": 0,
            "limit:": 100
        }
        nextStr = self.apiUrl + "playlists/" + playlist_id + "/tracks"
        track_list = list()
        while True:
            data = await self.session.get(nextStr, params=payload, headers=self.headers)
            if data.ok:
                json = await data.json()
                for i in json['items']:
                    track_list.append({'track': i['track']["uri"], 'artist': i['track']['artists'][0]["uri"]})
                    # artists_list.append(i['track']['artists'][0]["uri"])
                if json['next'] is not None:
                    nextStr = json['next']
                else:
                    return track_list
            else:
                print("ERROR")
                return

    async def track_recommendation(self, parms):
        if "seed_artist" in parms.keys() or \
                "seed_genres" in parms.keys() or \
                "seed_tracks" in parms.keys():
            data = await self.session.get(self.apiUrl + "recommendations", params=parms, headers=self.headers)
            js = await data.json()
            if data.ok:
                return js
            else:
                print(js['error'])
                return dict()
        else:
            print("Seed artists, genres, or tracks required")
            return None

    async def related_artists(self, id):
        data = await self.session.get(self.apiUrl + "artists/{}/related-artists".format(id), headers=self.headers)
        artists_list = []

        if data.ok:
            dataJson = await data.json()
            for i in dataJson['artists']:
                item = dict()
                item['artist'] = i['id']
                item['genres'] = i['genres']
                artists_list.append(item)
            return artists_list
        else:
            print(data)
            return []

    async def get_artist_genre(self, id):
        data = await self.session.get(self.apiUrl + "artists/{}".format(id), headers=self.headers)

        if data.ok:
            js = await data.json()
            return js['genres']
        else:
            print(data)
            return []

    async def get_artist_name(self, id):
        data = await self.session.get(self.apiUrl + "artists/{}".format(id), headers=self.headers)

        js = await data.json()
        if data.ok:
            return js['name']
        else:
            print(js['error'])
            return ""

    async def create_playlist(self, id, name, tracks=[], public=True, decription=None):
        body = {
            "name": name,
            "public": str(public)
        }
        if decription is not None:
            body["description"] = decription

        response = await self.session.post(self.apiUrl + "users/" + id + '/playlists', json=body, headers=self.headers)
        playlistId = (await response.json())['id']

        uris = list()
        counter = 0
        for i in tracks:
            if counter != 100:
                uris.append(i)
                counter += 1
            else:
                response1 = await self.session.post(self.apiUrl + "playlists/" + playlistId + '/tracks',
                                                    json={"uris": uris, 'position': '0'}, headers=self.headers)

                if not response1.ok:
                    error = json.loads(await response1.reason)
                    print(error['error'] + ': ' + error['error_description'])
                    return

                uris = list()
                counter = 0

        if len(uris) != 0:
            response1 = await self.session.post(self.apiUrl + "playlists/" + playlistId + '/tracks',
                                                json={"uris": uris, 'position': '0'}, headers=self.headers)

            if not response1.ok:
                error = json.loads(response1.reason)
                print(error['error'] + ': ' + error['error_description'])


async def similar_artists(spotify, artists) -> list:
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
                related1 = await spotify.related_artists(id1)
                related2 = await spotify.related_artists(id2)
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
            await asyncio.sleep(1)

        g1 = await spotify.get_artist_genre(id1)
        for z in lightSim:
            item = z.split(":")[2]
            g2 = await spotify.get_artist_genre(item)
            setg1 = set(g1)
            setg2 = set(g2)
            if Jaccard(setg1, setg2) > 0.124:
                uniqeArtists[uniqeArtists.index(z)] = ""
                sim.append(z)
            await asyncio.sleep(1)

        listSim.append(sim)
    """    
    for i in listSim:
        for j in i:
            if j != i[0]:
                print("     " + j)
            else:
                print(j)
    """
    return listSim


async def average_audio_features(spotify, data) -> dict:
    tracks_features = list()
    for i in data:
        i = i['track'].split(':')[2]
        try:
            features = await (await spotify.audio_features(i)).json()
            if 'error' not in features.keys():
                features_json = dict()
                features_json['energy'] = features["energy"]
                features_json['loud'] = features["loudness"]
                features_json["dance"] = features["danceability"]
                features_json["speech"] = features["speechiness"]
                features_json["valence"] = features["valence"]
                features_json["uri"] = features["uri"]
                tracks_features.append(features_json)
                # print(i + ' checked')
            else:
                print(features['error'])
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
        try:
            aver_features[key] = sum_features[key] / count
        except Exception as e:
            print(e)
            return dict()
    return aver_features


async def playlist_recommnedation_tracks(spotify, data, sim_artists, aver_features, limit, market) -> list:
    full_uris = list()
    for artists in sim_artists:
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
                    "limit": limit,
                    "market": market
                }

                rec_data = await spotify.track_recommendation(params)
                uris = listOfTracks(rec_data)
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

            rec_data = await spotify.track_recommendation(params)
            uris = listOfTracks(rec_data)
            full_uris.extend(list(set(uris).difference(set(full_uris))))

    return full_uris


async def create_based_playlist(spotify, playlist_id, name, public=True, desc="", baseOnMarket=False, limit=5):
    userData = await spotify.get_user_info()
    userId = userData['id']

    market = "US"
    if baseOnMarket:
        market = userData['country']

    data = await spotify.get_playlist_tracks(playlist_id)

    artists = list()

    for i in data:
        artists.append(i['artist'])

    similars = await similar_artists(spotify, artists)

    aver_features = await average_audio_features(spotify, data)

    full_uris = await playlist_recommnedation_tracks(spotify, data, similars, aver_features, limit, market)

    await spotify.create_playlist(userId, name, full_uris, public, desc)