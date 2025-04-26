from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.reply import main_menu

def register_base_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer("🏷️ Бот для мониторинга скинов CS2\nВыберите действие:", reply_markup=main_menu())

    @dp.message(F.text == "Назад в меню")
    async def cmd_back(message: Message,state: FSMContext):
        await state.clear()
        await message.answer("🏷️ Бот для мониторинга скинов CS2\nВыберите действие:", reply_markup=main_menu())