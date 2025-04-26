from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user_states import Form
from utils.validation import validate_cookies
import json


def register_cookies_handlers(dp):
    @dp.message(F.text == "Обновить куки")
    async def update_cookies(message: Message, state: FSMContext):
        await state.set_state(Form.waiting_cookies)
        await message.answer("Отправьте файл cookies.json с обновленными куки:")

    @dp.message(Form.waiting_cookies, F.document)
    async def handle_cookies_file(message: Message, state: FSMContext):
        file = await message.bot.get_file(message.document.file_id)
        await message.bot.download_file(file.file_path, destination="cookies.json")
        try:
            data = json.loads(open("cookies.json", 'r', encoding='utf-8').read())
            if not validate_cookies(data):
                raise ValueError
            await message.answer("✅ Куки обновлены!")
        except:
            await message.answer("❌ Некорректный файл куки!")
        finally:
            await state.clear()