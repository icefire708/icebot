from cities import CITIES
from settings import SMILES
from emoji import emojize
from random import choice
from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_smile(smile_type: str = 'good') -> str:
    if smile_type not in SMILES:
        smile_type = 'good'
    smile = choice(SMILES[smile_type])
    return emojize(smile, use_aliases=True)


def last_letter(city: str) -> None:
    for letter in reversed(city):
        if letter in CITIES:
            return letter

def next_city(letter: str, used_cities: set) -> str:
    for city in CITIES[letter]:
        if city not in used_cities:
            return city
    return '' # кончились города у ПК

def main_keyboard():
    keyboard = [
        ['города', 'в каком созвездии'],
        ['котики', 'помогатор', KeyboardButton('мои координаты', request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard)

# TODO что-то сделать с кодом ниже, мне оно не нравится так и тут
from telegram.update import Update
def game_over(update: Update, used_cities: set, letter: str) -> None:
    used_cities = set() # del?
    update.message.reply_text(f"Городов на букву {letter} больше не знаю. ТЫ ПОБЕДИЛ!")
