from source.Bot.BotHandler import *

import asyncio
from source.spotify.SpotifyRequest import parseUrlParams
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

handler = HelloHandler()
handler1 = AuthHandler()
handler2 = PlaylistHandler()

bot.add_handler(handler)
bot.add_handler(handler1)
bot.add_handler(handler2)


async def check_auth(request):
    print("AUTH GET!")
    url = request.url
    auth_data = parseUrlParams(url)
    auth_data['type'] = 'auth'
    bot.procceed_updates([auth_data])
    return web.Response()

async def check(request):
    print("MESSAGE GET!")
    js = await request.json()
    bot.procceed_updates([js])
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
            app.router.add_get("/callback/", check_auth)
            web.run_app(app, host="0.0.0.0", port=PORT)

        else:
            print("WEBHOOK NOT OK: " + status)
            config["isWebHookOk"] = 0
            conf_file = open("source/Bot/bot_config.json", "w")
            json.dump(config, conf_file)
            conf_file.close()
    else:
        print("LOCAL MACHINE")
        status = bot.delete_webhook()
        if status:
            config["isWebHookOk"] = 0
            conf_file = open("Bot/bot_config.json", "w")
            json.dump(config, conf_file)
            conf_file.close()
            while True:
                updates = bot.getUpdates()
                if updates is not None:
                    bot.procceed_updates(updates)
        else:
            print(status)