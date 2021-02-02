from Bot.BotHandler import *

if __name__ == "__main__":
    bot = BotHandler()
    while True:
        updates = bot.getUpdates()
        if updates is not None:
            for i in updates:
                if i["message"]["from"]["username"] == "piligrimvstheworld":
                    bot.sendMessage(i["message"]["from"]["id"], "Вы лучший, создатель!")
                if i["message"]["from"]["username"] == "freindlih":
                    bot.sendMessage(i["message"]["from"]["id"], "Пока что я не очень разбираюсь в человеческой речи и не все понимаю, но мой создатель сказал, что очень вас любит!")
