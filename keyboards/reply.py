from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

__all__ = ["main_menu", "back_menu"]

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Добавить скин'), KeyboardButton(text='Удалить скин')],
            [KeyboardButton(text='Просмотреть скины'), KeyboardButton(text='Начать мониторинг')],
            [KeyboardButton(text='Обновить куки')]
        ],
        resize_keyboard=True
    )

def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Назад в меню')]],
        resize_keyboard=True
    )
