import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

def greet_user(update, context):
    print('Вызван /start')
    update.message.reply_text('Привет, пользователь! Ты вызвал команду /start')

def talk_to_me(update, context):
    user_text = update.message.text        
    print(user_text) 
    if '?' in user_text:
        update.message.reply_text('На вопросы не отвечаю')
    else:
        update.message.reply_text(f'Ты написал: {user_text}!!!!!!!111111111')

def main():
    mybot = Updater(settings.token, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info("Bot is working!")
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()