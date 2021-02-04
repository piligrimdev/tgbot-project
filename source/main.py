from Bot.BotHandler import *

import asyncio
from aiohttp import web
import os
import json

PORT = int(os.environ.get('PORT', 5000))
config = ""
if os.environ.get("HEROKU") is not None:
    with open("source/Bot/bot_config.json", "r") as conf_file:
        config = json.load(conf_file)
        config["webhook_port"] = str(PORT)
else:
    with open("Bot/bot_config.json", "r") as conf_file:
        config = json.load(conf_file)
        config["webhook_port"] = "8443"

bot = BotHandler(config)

async def check(request):
    print("MESSAGE GET!")
    return web.Response()

if __name__ == "__main__":
    status = ""
    if os.environ.get("HEROKU") is not None:
        status = bot.check_webhook()
        if status == True:
            print("WEBHOOK OK")
            config["isWebHookOk"] = 1
            conf_file = open("source/Bot/bot_config.json", "w")
            json.dump(config, conf_file)
            conf_file.close()


            app = web.Application()
            app.router.add_post("/" + config["token"] + "/", check)
            web.run_app(app, host="0.0.0.0", port=PORT)



        else:
            print(status)
    else:
        print("WEBHOOK NOT OK:  " + status)
        while True:
            updates = bot.getUpdates()
            if updates is not None:
                for i in updates:
                    bot.sendMessage(i["message"]["from"]["id"], "test")