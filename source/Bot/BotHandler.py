import json
import requests
import asyncio
import aiohttp

class BotHandler:
    def __init__(self, conf):

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