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
    id = input()
    data = client.similar_artist(id)
    data = data.json()
    print(data['tracks'][10]['artists'][0]['external_urls']['spotify'])