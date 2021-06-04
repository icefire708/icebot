import logging
from my_token import TG_API_TOKEN
from handlers import COMMANDS, talk_to_me, coordinates
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(filename='bot.log', level=logging.INFO)

def main() -> None:
    mybot = Updater(TG_API_TOKEN, use_context=True)

    for command, info_tuple in COMMANDS.items():
        mybot.dispatcher.add_handler(CommandHandler(command, info_tuple[0]))
        mybot.dispatcher.add_handler(MessageHandler(Filters.regex(f'^({info_tuple[1]})$'), info_tuple[0]))
    mybot.dispatcher.add_handler(MessageHandler(Filters.location, coordinates))
    mybot.dispatcher.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info("Bot is working!")
    print("Всё ок, бот работает!")
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
