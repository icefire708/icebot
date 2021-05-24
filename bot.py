import logging
import ephem
import settings
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from difflib import get_close_matches
from datetime import date
from constellations import constellations

logging.basicConfig(filename='bot.log', level=logging.INFO)

GREET_TEXT = '''Привет!
Я самый лучший бот на свете.'''

PLANETS = ('Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune')

def planet(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text.lower()
    user_data = user_text.split()
    if user_text == '/planet':
        update.message.reply_text('Напиши через пробел после команды название планеты. К примеру:\n/planet Mars')
    elif len(user_data) != 2:
        update.message.reply_text('Напиши через пробел после команды название ОДНОЙ планеты. К примеру:\n/planet Saturn')
    else:
        planet = user_data[1].capitalize()
        if planet == 'Earth':
            update.message.reply_text('Мы сейчас на этой планете, не знал?)')
            return
        if planet == 'Moon':
            update.message.reply_text('Это спутник, а не планета, ну да ладно.')
        if planet != 'Moon' and planet not in PLANETS:
            close_match = get_close_matches(planet, PLANETS, n=1)
            if close_match:
                update.message.reply_text(f'Вероятно ты имел в виду {close_match[0]}, а не {planet}.')
                planet = close_match[0]
            else:
                update.message.reply_text(f'Зацени какие планеты доступны: ' + ', '.join(PLANETS))
                return
        body = getattr(ephem, planet)
        day = date.today()
        constellation = ephem.constellation(body(day))[1]
        constellation_rus, constellation_ukr = constellations[constellation]
        update.message.reply_text(f'{planet} в созвездии {constellation} ({constellation_rus}/{constellation_ukr}).')

def greet_user(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(GREET_TEXT)
    help(update, context)

def help(update: Update, context: CallbackContext) -> None:
    out =''
    for key, value in COMMANDS.items():
        out += f'/{key} -- {value[1]}\n'
    update.message.reply_text(out)

def talk_to_me(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    if '?' in user_text:
        update.message.reply_text('На вопросы не отвечаю')
    else:
        update.message.reply_text(f'Ты написал: {user_text}!!!!!!!111111111')

def calc(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text[len('/calc'):].replace(' ', '').replace(',', '.').replace('^', '**').replace(':', '/')
    if not user_text:
        update.message.reply_text('Напиши через пробел после команды арифметическое выражения и я его вычислю. К примеру:\n/calc 2 + 2 * 2')
        return
    legal_simvols = set('.%+-*/()0123456789')
    if not set(user_text).issubset(legal_simvols):
        update.message.reply_text('Это какая-то шляпа, а не арифметическое выражение')
        return
    try:
        result = eval(user_text)
        update.message.reply_text(f'{user_text} = {result}')
    except SyntaxError:
        update.message.reply_text('Ты написал с ошибками, не могу вычислить')
    except ZeroDivisionError:
        update.message.reply_text('НЕ СМЕЙ ДЕЛИТЬ НА НОЛЬ!')

def cities(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Я пока не работаю!')

COMMANDS = {
    'start': (greet_user, 'приветсвтвие'), 
    'planet': (planet, 'в каком созвездии'), 
    'help': (help, 'помогатор'), 
    'calc': (calc, 'калькулятор'), 
    'cities': (cities, 'игруля города'),
}

def main() -> None:
    mybot = Updater(settings.token, use_context=True)

    for command, info_tuple in COMMANDS.items():
        mybot.dispatcher.add_handler(CommandHandler(command, info_tuple[0]))
    mybot.dispatcher.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info("Bot is working!")
    print("Всё ок, бот работает!")
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
