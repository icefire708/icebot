from telegram import bot
from cities import CITIES
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

PLANETS = ('Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune')

SMILES = {
    'good': (':fire:', ':smile:', ':smiling_imp:', ':innocent:', ':thumbsup:'),
    'bad': (':imp:', ':rage:', ':expressionless:', ':unamused:', ':confused:'),
    'cat': (':smiley_cat:', ':smile_cat:', ':smirk_cat:', ':scream_cat:', ':joy_cat:'),
}

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

def get_smile(smile_type: str = 'good') -> str:
    if smile_type not in SMILES:
        smile_type = 'good'
    smile = choice(SMILES[smile_type])
    return emojize(smile, use_aliases=True)

def greet_user(update: Update, context: CallbackContext) -> None:
    smile = get_smile()
    user_name = update.effective_user.first_name
    update.message.reply_text(f'Привет, {user_name}! Я самый лучший бот на свете {smile}')
    help(update, context)

def help(update: Update, context: CallbackContext) -> None:
    out =''
    for key, value in COMMANDS.items():
        out += f'/{key} -- {value[1]}\n'
    update.message.reply_text(out)

def talk_to_me(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    if '?' in user_text:
        smile = get_smile('bad')
        update.message.reply_text(f'На вопросы не отвечаю {smile}')
    else:
        update.message.reply_text(f'Ты написал: {user_text}!!!!!!!111111111')

def calc(update: Update, context: CallbackContext) -> None:
    # TODO /calc 7**888**888**888888888888888**888888888 через трерды следить и убивать?
    # TODO /calc ()
    # TODO /calc ()()
    # TODO мб переписать обработку аргументов
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

def last_letter(city: str) -> None:
    for letter in reversed(city):
        if letter in CITIES:
            return letter

def next_city(letter: str, used_cities: set) -> str:
    for city in CITIES[letter]:
        if city not in used_cities:
            return city
    return '' # кончились города у ПК

def game_over(update: Update, used_cities: set, letter: str) -> None:
    used_cities = set()
    update.message.reply_text(f"Городов на букву {letter} больше не знаю. ТЫ ПОБЕДИЛ!")

def cities(update: Update, context: CallbackContext) -> None:
    # TODO упростить функцию и разнести на более мелкие
    if len(context.args) == 1:
        city = context.args[0].lower()
        if context.user_data.get('used_cities'):
            if city[0] not in CITIES or city not in CITIES[city[0]]:
                msg = f"Такого города не знаю, введите город на букву{context.user_data['last_letter']}"
                update.message.reply_text(msg)
            elif city in context.user_data['used_cities']:
                update.message.reply_text('Увы такой город уже был')
            else:
                context.user_data['used_cities'].add(city)
                bot_city = next_city(last_letter(city), context.user_data['used_cities'])
                if not bot_city:
                    game_over(update, context.user_data['used_cities'], last_letter(city))
                    return
                context.user_data['used_cities'].add(bot_city)
                msg_part_1 = f'Мой город: {bot_city.title()}\n'
                context.user_data['last_letter'] = last_letter(bot_city).upper()
                msg_part_2 = f'Тебе на букву {context.user_data["last_letter"]}'
                update.message.reply_text(msg_part_1 + msg_part_2)
        elif city[0] not in CITIES or city not in CITIES[city[0]]:
            update.message.reply_text("Такого города не знаю")
        else:
            context.user_data['used_cities'] = set()
            context.user_data['used_cities'].add(city)
            bot_city = next_city(last_letter(city), context.user_data['used_cities'])
            context.user_data['used_cities'].add(bot_city)
            msg_part_1 = f'Мой город: {bot_city.title()}\n'
            context.user_data['last_letter'] = last_letter(bot_city).upper()
            msg_part_2 = f'Тебе на букву {context.user_data["last_letter"]}'
            update.message.reply_text(msg_part_1 + msg_part_2)
    elif context.args:
        msg = "Тебе следует вводить название одного города.\nВо вводе только один пробел после /cities"
        update.message.reply_text(msg)
    elif context.user_data.get('used_cities'):
        update.message.reply_text(f"Введи /cities и город на букву {context.user_data['last_letter']}")
    else:
        update.message.reply_text(f"Для старта игры введи /cities и любой существующий в этом мире город")

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
    context.bot.send_photo(chat_id=chat_id, photo=open(cat, 'rb'), caption=get_smile('cat'))

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
