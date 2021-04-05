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
    def __init__(self):
        self.onStatus = 0
        self.onString = ""

    def handle(self, bot, message):
        bot.sendMessage(message['from']['id'], "Привет, {}!".format(message['from']['username']))
        bot.sendMessage(message['from']['id'], "Я - бот, который подберет тебе плейлист на основе твоего плейлиста")
        bot.sendMessage(message['from']['id'], "Для начала, мне нужно авторизовать тебя в Spotify")

        with  open(sys.path[0] + "/spotify/spotify_config.json", "r") as file:
            conf = json.load(file)
        spotify = Spotify(0.2)
        link = spotify.getAuthLink(conf, "https://tgbotproject.herokuapp.com/callback/",
                                   'playlist-modify-public', message['from']['id'])
        bot.sendMessage(message['from']['id'], link)

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
    def __init__(self):
        self.onStatus = 0
        self.onString = ""

    def handle(self, bot, message):

        with  open(sys.path[0] + "/spotify/spotify_config.json", "r") as file:
            conf = json.load(file)
        spotify = bot.user_spotify[message['state']]

        spotify.userAuth(conf, "https://tgbotproject.herokuapp.com/callback/", message['code'])

        bot.sendMessage(message['from']['id'], "Отлично, я тебя запомнил!")
        bot.sendMessage(message['from']['id'], "Теперь, пришли мне, пожалуйста, Spotify URI на плейлист, который ты хочешь положить в основу нового")

        bot.dialog_status[message['from']['id']] += 1

    def canHandle(self, bot, message):
        if 'type' in message.keys() and 'state' in message.keys():
            if message['state'] in bot.user_spotify.keys():
                return True
        return False


class PlaylistHandler:
    def __init__(self):
        self.onStatus = 2
        self.onString = ""

    def handle(self, bot, message):
        uri = message['text']
        bot.sendMessage(message['from']['id'], "Отлично! Совсем скоро будет готов плейлист!")
        uri = uri.split(":")[2]
        spotify = bot.user_spotify[message['from']['id']]
        create_based_playlist(spotify, uri, "MEGA TEST 10")
        bot.sendMessage(message['from']['id'], "Проверь свой профиль Spotify, ведь там тебя ждет плейлист MEGA TEST 10!")
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
        self.dialog_status = {}
        self.user_spotify = {}
        self.config = conf
        self.url = "https://api.telegram.org/bot" + self.config["token"] + "/"
        self.lastUpdateId = self.config["lastUpdateId"]
        self.debug = self.config["lastUpdateId"]
        self.session = requests.Session()

    def getUpdates(self):
        update = self.session.get(self.url + "getUpdates")
        update = update.json()
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

    def procceed_updates(self, updates):
        for i in updates:
            if 'message' in i.keys():
                for j in self.handlers:
                    if j.canHandle(self, i['message']):
                        j.handle(self, i['message'])
                        break
            elif 'type' in i.keys():
                for j in self.handlers:
                    if j.canHandle(self, i):
                        j.handle(self, i)
                        break

    def sendMessage(self, id, text):
        return self.session.post(self.url + "sendMessage", {"chat_id": id, "text": text})

    def check_webhook(self):
        print("Checking webhook in file")
        if self.config["isWebHookOk"] == 1:
            print("     File says its ok")
            status = self.session.get(self.url + "getWebhookInfo")
            status = status.json()
            print(status)
            if status["ok"] == True:
                return True
            else:
                return False
        else:
            print("     Its not ok in file")
            status = self.session.get(self.url + "setWebhook?url=" + self.config["webhook_url"] + "/" + self.config["token"] + "/")
            status = status.json()
            print(status)
            if status["ok"] == True:
                return True
            else:
                return status["error_code"]

    def delete_webhook(self):
        status = self.session.get(self.url + "getWebhookInfo")
        status = status.json()
        if status["ok"] == True:
            status = self.session.get(self.url + "deleteWebhook")
            status= status.json()
            if status["ok"] == True:
                return True
            else:
                return status["error_code"]
        else:
            return True