from cities import CITIES
import ephem
from constellations import constellations_translate
from random import randint, choice
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from difflib import get_close_matches
from datetime import date
from glob import glob
from utils import get_smile, main_keyboard, next_city, last_letter, game_over
from settings import PLANETS


def cat(update: Update, context: CallbackContext) -> None:
    cats_list = glob('images/cat*.jp*g')
    cat = choice(cats_list)
    chat_id = update.effective_chat.id    
    context.bot.send_photo(chat_id=chat_id, photo=open(cat, 'rb'), caption=get_smile('cat'))

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

def cities(update: Update, context: CallbackContext) -> None:
    # TODO мб упростить функцию и разнести на более мелкие
    if context.args and len(context.args) == 1:
        city = context.args[0].lower()
        if context.user_data.get('used_cities'):
            if city[0] not in CITIES or city not in CITIES[city[0]]:
                msg = f"Такого города не знаю, введите город на букву {context.user_data['last_letter']}"
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

def greet_user(update: Update, context: CallbackContext) -> None:
    smile = get_smile()
    user_name = update.effective_user.first_name
    update.message.reply_text(f'Привет, {user_name}! Я самый лучший бот на свете {smile}', reply_markup=main_keyboard())
    help(update, context)

def help(update: Update, context: CallbackContext) -> None:
    out =''
    for key, value in COMMANDS.items():
        out += f'/{key} -- {value[1]}\n'
    update.message.reply_text(out, reply_markup=main_keyboard())

def talk_to_me(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    if '?' in user_text:
        smile = get_smile('bad')
        update.message.reply_text(f'На вопросы не отвечаю {smile}')
    else:
        update.message.reply_text(f'Ты написал: {user_text}!!!!!!!111111111')

def calc(update: Update, context: CallbackContext) -> None:
    # TODO /calc 7**888**888**888888888888888**888888888 через трерды следить и убивать?
    user_text = ''.join(context.args)
    user_text = user_text.replace(' ', '').replace(',', '.').replace('^', '**').replace(':', '/')
    if not user_text:
        update.message.reply_text('Напиши через пробел после команды арифметическое выражения и я его вычислю. К примеру:\n/calc 2 + 2 * 2')
        return
    digits = set('0123456789')
    legal_simvols = set('.%+-*/()') | digits
    input_simbols = set(user_text)
    if not (digits & input_simbols):
        update.message.reply_text('Ты не ввёл ни одной цифры')
        return
    if not input_simbols.issubset(legal_simvols):
        update.message.reply_text('Это какая-то шляпа, а не арифметическое выражение')
        return
    try:
        result = eval(user_text)
        update.message.reply_text(f'{user_text} = {result}')
    except (SyntaxError, TypeError):
        update.message.reply_text('Ты написал с ошибками, не могу вычислить')
    except ZeroDivisionError:
        update.message.reply_text('НЕ СМЕЙ ДЕЛИТЬ НА НОЛЬ!')

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
        constellation_rus, constellation_ukr = constellations_translate[constellation]
        update.message.reply_text(f'{planet} в созвездии {constellation} ({constellation_rus}/{constellation_ukr}).')

def coordinates(update: Update, context: CallbackContext) -> None:
    coords = update.message.location
    update.message.reply_text(f'Ваши координаты: {coords}')

COMMANDS = {
    'start': (greet_user, 'приветствие'), 
    'planet': (planet, 'в каком созвездии'), 
    'help': (help, 'помогатор'), 
    'calc': (calc, 'калькулятор'), 
    'cities': (cities, 'города'),
    'guess': (guess, 'угадайка'),
    'cat': (cat, 'котики'),
}
