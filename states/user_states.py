from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_link = State()
    waiting_float = State()
    waiting_percent = State()
    waiting_delete = State()
    waiting_cookies = State()