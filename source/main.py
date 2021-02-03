from Bot.BotHandler import *

import asyncio
import aiohttp
import os
import json

with open("Bot/bot_config.json", "r") as conf_file:
    config = json.load(conf_file)
bot = BotHandler(config)

def check():
    print("MESSAGE GET!")

if __name__ == "__main__":
    status = ""
    if os.environ.get("HEROKU") is not None:
        status = bot.check_webhook()
        if status == True:
            print("WEBHOOK OK")
            config["isWebHookOk"] = 1
            json.dumps(config, conf_file)
            app = aiohttp.web.Application()
            app.router.add_post("/" + config["token"] + "/", check)
            aiohttp.web.run_app(app, config["webhook_url"], config["webhook_port"])
    else:
        print("WEBHOOK NOT OK:  " + status)
        while True:
            updates = bot.getUpdates()
            if updates is not None:
                for i in updates:
                    bot.sendMessage(i["message"]["from"]["id"], "test")