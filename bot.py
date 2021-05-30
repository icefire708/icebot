import logging
import ephem
import settings
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from difflib import get_close_matches
from datetime import date
from constellations import constellations
from random import randint, choice
from glob import glob
from emoji import emojize

logging.basicConfig(filename='bot.log', level=logging.INFO)

GREET_TEXT = '''Привет!
Я самый лучший бот на свете.'''

PLANETS = ('Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune')

def planet(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Напиши через пробел после команды название планеты. К примеру:\n/planet Mars')
    elif len(context.args) != 1:
        update.message.reply_text('Напиши через пробел после команды название ОДНОЙ планеты. К примеру:\n/planet Saturn')
    else:
        planet = context.args[0].capitalize()
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
    '''
    TODO /calc 7**888**888**888888888888888**888888888 через трерды следить и убивать?
    TODO /calc ()
    TODO /calc ()()
    TODO мб переписать обработку аргументов
    '''
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

def guess(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 1 and context.args[0].isdigit():
        player_num = int(context.args[0])
        bot_num = randint(player_num - 21, player_num + 23)
        if player_num > bot_num:
            pre_text = 'Ты молниеносно победил!'
        elif player_num == bot_num:
            pre_text = 'Справедливая ничья.'
        else:
            pre_text = 'Вы позорно проиграли...'
        update.message.reply_text(f'{pre_text} Твоё число: {player_num}. Число бота: {bot_num}')
    else:
        update.message.reply_text('Напиши одно целое число через пробел после команды.\nК примеру:\n/guess 69')

def cat(update: Update, context: CallbackContext) -> None:
    cats_list = glob('images/cat*.jp*g')
    cat = choice(cats_list)
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(cat, 'rb'))

COMMANDS = {
    'start': (greet_user, 'приветствие'), 
    'planet': (planet, 'в каком созвездии'), 
    'help': (help, 'помогатор'), 
    'calc': (calc, 'калькулятор'), 
    'cities': (cities, 'игруля города'),
    'guess': (guess, 'своего рода игра со случайностью'),
    'cat': (cat, 'картинки с котиками'),
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
