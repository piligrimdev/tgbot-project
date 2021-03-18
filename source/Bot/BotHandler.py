import json
import requests
import asyncio
import aiohttp

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
        bot.sendMessage(message['from']['id'], "Hello There, {}!".format(message['from']['username']))
    def canHandle(self, bot, message):
        if message['from']['id'] in bot.dialog_status.keys():
            if self.onString in message['text'] and bot.dialog_status[message['from']['id']] == self.onStatus:
                return True
            else:
                return False
        else:
            bot.dialog_status[message['from']['id']] = 1
            return True

class HowHandler:
    def __init__(self):
        self.onStatus = 1
        self.onString = ""
    def handle(self, bot, message):
        bot.sendMessage(message['from']['id'], "How are you, {}?".format(message['from']['username']))
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

    def sendMessage(self, id, text):
        return self.session.post(self.url + "sendMessage", {"chat_id": id, "text": text})

    def check_webhook(self):
        if self.config["isWebHookOk"] == 1:
            status = self.session.get(self.url + "getWebhookInfo")
            status = status.json()
            if status["ok"] == True:
                return True
            else:
                return False
        else:
            status = self.session.get(self.url + "setWebhook?url=" + self.config["webhook_url"] + "/" + self.config["token"] + "/")
            status = status.json()
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