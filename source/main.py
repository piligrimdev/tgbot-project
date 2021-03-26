from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import json

from source.spotify.SpotifyRequest import create_based_playlist

if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    spotify = Spotify(0.2)
    if spotify.userAuth(conf, 'localhost', 8080, 'http://localhost:8080/', 'playlist-modify-public'):
        create_based_playlist(spotify, "3bSjIwakzyBHIljtQhmHs7", "Test 9.5")
