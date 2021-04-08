from source.Bot.BotHandler import *

import asyncio
from aiohttp import web
import os
import json

PORT = int(os.environ.get('PORT', 5000))
config = ""

def query_val(url : str) -> dict:
    values = dict()
    if len(url) != 0:
        if url.find('?') != -1:
            query = url.split('?')[1]
            values_pairs = query.split('&')
            for i in values_pairs:
                splited = i.split('=')
                values[splited[0]] = splited[1]
    return values


if os.environ.get("HEROKU") is not None:
    with open("source/Bot/bot_config.json", "r") as conf_file:
        config = json.load(conf_file)
        config["webhook_port"] = str(PORT)
else:
    with open("Bot/bot_config.json", "r") as conf_file:
        config = json.load(conf_file)
        config["webhook_port"] = "8443"

bot = BotHandler(config)

handler2 = PlaylistHandler()

bot.add_handler(handler2)


async def check_auth(request):
    print("AUTH GET!")
    print(request.rel_url)
    url = str(request.rel_url)
    auth_data = query_val(url)
    auth_data['type'] = 'auth'
    await bot.procceed_updates([auth_data])
    return web.Response()

async def check(request):
    print("MESSAGE GET!")
    js = await request.json()
    await bot.procceed_updates([js])
    return web.Response()


async def main(loop):
    status = ""
    bot.set_loop = loop
    if os.environ.get("HEROKU") is not None:
        status = await bot.check_webhook()
        if status == True:

            handler = HelloHandler("https://tgbotproject.herokuapp.com/callback/")
            bot.add_handler(handler)
            handler1 = AuthHandler("https://tgbotproject.herokuapp.com/callback/")
            bot.add_auth_handler(handler1)

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
        status = await bot.delete_webhook()
        if status:
            config["isWebHookOk"] = 0
            conf_file = open("Bot/bot_config.json", "w")
            json.dump(config, conf_file)
            conf_file.close()

            handler = LocalHelloHandler('localhost', 8080, "https://localhost:8080/")
            bot.add_handler(handler)
            while True:
                updates = await bot.getUpdates()
                if updates is not None:
                    await bot.procceed_updates(updates)
        else:
            print(status)
if __name__ == "__main__":
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(main(ioloop))
    ioloop.close()