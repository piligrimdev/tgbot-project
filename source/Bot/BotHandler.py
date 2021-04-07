import json
import requests
import asyncio
import aiohttp
import sys
from source.spotify.SpotifyRequest import *

class HandlerMeta(type):
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'handle') and
                callable(subclass.handle) and
                hasattr(subclass, 'canHandle') and
                callable(subclass.canHandle))

class BaseHandler(metaclass=HandlerMeta):
    def __init__(self):
        self.onStatus = 0
        self.onString = ""
    def handle(self,bot, message):
        pass
    def canHandle(self, bot, message) -> bool:
        pass

class HelloHandler:
    def __init__(self, url):
        self.onStatus = 0
        self.onString = ""
        self.url = url
    async def handle(self, bot, message):
        print('In ' + str(type(self)) + "for id: " + str(message['from']['id']))
        if 'username' in message['from'].keys():
            greetStr = "Привет, {}!".format(message['from']['username'])
        else:
            greetStr = "Привет!"
        await bot.sendMessage(message['from']['id'], greetStr)
        await bot.sendMessage(message['from']['id'], "Я - бот, который подберет тебе плейлист на основе твоего плейлиста")
        await bot.sendMessage(message['from']['id'], "Для начала, мне нужно авторизовать тебя в Spotify")

        with open(sys.path[0] + "/spotify/spotify_config.json", "r") as file:
            conf = json.load(file)

        spotify = Spotify()
        link = await spotify.getAuthLink(conf, self.url,
                                   'playlist-modify-public', message['from']['id'])
        await bot.sendMessage(message['from']['id'], str(link))

        bot.user_spotify[message['from']['id']] = spotify

    def canHandle(self, bot, message):
        if message['from']['id'] in bot.dialog_status.keys():
            if self.onString in message['text'] and bot.dialog_status[message['from']['id']] == self.onStatus:
                return True
            else:
                return False
        else:
            bot.dialog_status[message['from']['id']] = 1
            return True

class AuthHandler:
    def __init__(self, url):
        self.onStatus = 0
        self.onString = ""
        self.url = url
    async def handle(self, bot, message):
        print('In ' + str(type(self)) + "for id: " + str(message['from']['id']))
        with  open(sys.path[0] + "/spotify/spotify_config.json", "r") as file:
            conf = json.load(file)
        spotify = bot.user_spotify[int(message['state'])]

        await spotify.userAuth(conf, self.url, message['code'])

        await bot.sendMessage(message['state'], "Отлично, я тебя запомнил!")
        await bot.sendMessage(message['state'], "Теперь, пришли мне, пожалуйста, Spotify URI на плейлист, который ты хочешь положить в основу нового")

        bot.dialog_status[int(message['state'])] += 1

    def canHandle(self, bot, message):
        return True


class PlaylistHandler:
    def __init__(self):
        self.onStatus = 2
        self.onString = ""

    async def handle(self, bot, message):
        print('In ' + str(type(self)) + "for id: " + str(message['from']['id']))
        uri = message['text']
        await bot.sendMessage(message['from']['id'], "Отлично! Совсем скоро будет готов плейлист!")
        uri = uri.split(":")[2]
        spotify = bot.user_spotify[message['from']['id']]
        await create_based_playlist(spotify, uri, "MEGA TEST 10")
        await bot.sendMessage(message['from']['id'], "Проверь свой профиль Spotify, ведь там тебя ждет плейлист MEGA TEST 10!")
        bot.dialog_status[message['from']['id']] += 1

    def canHandle(self, bot, message):
        if message['from']['id'] in bot.dialog_status.keys():
            if self.onString in message['text'] and bot.dialog_status[message['from']['id']] == self.onStatus:
                return True
            else:
                return False

class BotHandler:
    def __init__(self, conf):

        self.handlers = []
        self.auth_handlers = []
        self.dialog_status = {}
        self.user_spotify = {}
        self.config = conf
        self.url = "https://api.telegram.org/bot" + self.config["token"] + "/"
        self.lastUpdateId = self.config["lastUpdateId"]
        self.debug = self.config["lastUpdateId"]
        self.session = aiohttp.ClientSession()

    async def getUpdates(self):
        update = await self.session.get(self.url + "getUpdates")
        update = await update.json()
        if update["ok"] == True:
            if update["result"] != []:
                responses = update["result"]

                if self.debug == 1 and self.lastUpdateId == 0:
                    self.lastUpdateId = responses[len(responses) - 1]["update_id"]

                if self.lastUpdateId != responses[len(responses) - 1]["update_id"]:

                    new_responses = []
                    for i in responses:
                        if i["update_id"] > self.lastUpdateId:
                            new_responses.append(i)

                    self.lastUpdateId = responses[len(responses) - 1]["update_id"]

                    with open("Bot/bot_config.json", "w") as conf_file:
                        self.config["lastUpdateId"] = responses[len(responses) - 1]["update_id"]
                        json.dump(self.config, conf_file)

                    return new_responses

    def add_handler(self, handler):
            if issubclass(handler, BaseHandler):
                self.handlers.append(handler)
            else:
                print("{} is not fully implements BaseHandler interface".format(type(handler)))

    def add_auth_handler(self, handler):
        if issubclass(handler, BaseHandler):
            self.auth_handlers.append(handler)
        else:
            print("{} is not fully implements BaseHandler interface".format(type(handler)))

    async def procceed_updates(self, updates):
        for i in updates:
            if 'message' in i.keys():
                for j in self.handlers:
                    if j.canHandle(self, i['message']):
                        print('update from ' + str(i['message']['from']['id']))
                        await j.handle(self, i['message'])
                        break
            elif 'type' in i.keys():
                for j in self.auth_handlers:
                    if j.canHandle(self, i):
                        await j.handle(self, i)
                        break

    async def sendMessage(self, id, text):
        return await self.session.post(self.url + "sendMessage", params={"chat_id": id, "text": text})

    async def check_webhook(self):
        print("Checking webhook in file")
        if self.config["isWebHookOk"] == 1:
            print("     File says its ok")
            status = await self.session.get(self.url + "getWebhookInfo")
            status = await status.json()
            print(status)
            if status["ok"]:
                return True
            else:
                return False
        else:
            print("     Its not ok in file")
            status = await self.session.get(self.url + "setWebhook?url=" + self.config["webhook_url"] + "/" + self.config["token"] + "/")
            status = await status.json()
            print(status)
            if status["ok"]:
                return True
            else:
                return status["error_code"]

    async def delete_webhook(self):
        status = await self.session.get(self.url + "getWebhookInfo")
        status = await status.json()
        if status["ok"] == True:
            status = await self.session.get(self.url + "deleteWebhook")
            status = await status.json()
            if status["ok"] == True:
                return True
            else:
                return status["error_code"]
        else:
            return True