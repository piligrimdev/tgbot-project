from Bot.BotHandler import *
from spotify.SpotifyRequest import *
import asyncio
from aiohttp import web
import os
import json


if __name__ == "__main__":
    with open("spotify/spotify_config.json", "r") as file:
        conf = json.load(file)
    client = Spotify(conf)
    params = {
        "seed_tracks": "6VCq9JcEi9EbEKl8XIdCgk,7Fur0xdBxvYbIT3qNUtYT2",
        "min_energy": "0.75",
        "market": "US"
    }
    data = client.similar_artist(params)
    if data:
        data = data.json()
        print(data['tracks'][10]['artists'][0]['external_urls']['spotify'])