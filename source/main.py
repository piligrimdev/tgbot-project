from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import asyncio
from aiohttp import web
import os
import json



if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    spotify = Spotify()
    params = {
        "seed_tracks": "6VCq9JcEi9EbEKl8XIdCgk,7Fur0xdBxvYbIT3qNUtYT2",
        "min_energy": "0.75",
        "market": "US",
        "limit": "25"
    }
    if spotify.userAuth(conf, 'localhost', 8080, 'http://localhost:8080/', 'playlist-modify-public'):
        data = spotify.similar_artist(params)

    if data:
        data = data.json()
        list = listOfTracks(data)
     #   spotify.create_playlist("fgt0pmkaco3f1a5259n0ayqsa", "Test", list)
