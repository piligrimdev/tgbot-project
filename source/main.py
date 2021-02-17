from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import asyncio
from aiohttp import web
import os
import json



if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    client = Spotify(conf, True, "http://localhost:8080/")
    params = {
        "seed_tracks": "6VCq9JcEi9EbEKl8XIdCgk,7Fur0xdBxvYbIT3qNUtYT2",
        "min_energy": "0.75",
        "market": "US",
        "limit": "25"
    }
    data = client.similar_artist(params)
    if data:
        data = data.json()
        list = listOfTracks(data)
        client.create_playlist("fgt0pmkaco3f1a5259n0ayqsa", "Test", list)
