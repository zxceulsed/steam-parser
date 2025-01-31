from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Добавить скин'), KeyboardButton(text='Удалить скин')],
            [KeyboardButton(text='Просмотреть скины'), KeyboardButton(text='Начать мониторинг')],
            [KeyboardButton(text='Обновить куки')]
        ],
        resize_keyboard=True
    )

def back_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Назад в меню')]],
        resize_keyboard=True
    )