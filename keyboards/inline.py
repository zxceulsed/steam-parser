from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

__all__ = ["example_inline_keyboard"]

def example_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data='yes'),
                InlineKeyboardButton(text='Нет', callback_data='no')
            ]
        ]
    )