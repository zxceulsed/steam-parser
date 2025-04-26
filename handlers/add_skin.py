from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user_states import Form
from keyboards.reply import back_menu
from services.storage import load_skins, save_skins


def register_add_skin_handlers(dp: Dispatcher):
    @dp.message(F.text == "Добавить скин")
    async def add_skin(message: Message, state: FSMContext):
        await state.set_state(Form.waiting_link)
        await message.answer(
            "Отправьте ссылку на страницу скина с Steam Market:",
            reply_markup=back_menu()
        )

    @dp.message(Form.waiting_link)
    async def process_link(message: Message, state: FSMContext):
        url = message.text.strip()
        if not url.startswith('https://steamcommunity.com/market'):
            await message.answer("❌ Это не похоже на Steam Market ссылку!")
            return
        await state.update_data(link=url)
        await state.set_state(Form.waiting_float)
        await message.answer(
            "Теперь отправьте диапазон float в формате: 0.00-0.02",
            reply_markup=back_menu()
        )

    @dp.message(Form.waiting_float)
    async def process_float(message: Message, state: FSMContext):
        text = message.text.strip()
        try:
            min_f, max_f = map(float, text.split('-'))
            if min_f > max_f:
                await message.answer("❌ Минимальное значение должно быть меньше максимального!")
                return
        except:
            await message.answer("❌ Неверный формат! Используйте пример: 0.00-0.02")
            return
        await state.update_data(min_float=min_f, max_float=max_f)
        await state.set_state(Form.waiting_percent)
        await message.answer(
            "Введите максимальный допустимый процент превышения цены (например 20):",
            reply_markup=back_menu()
        )

    @dp.message(Form.waiting_percent)
    async def process_percent(message: Message, state: FSMContext):
        try:
            percent = float(message.text.strip())
            if percent <= 0:
                await message.answer("❌ Процент должен быть положительным числом!")
                return
        except:
            await message.answer("❌ Введите корректное числовое значение!")
            return
        data = await state.get_data()
        skins = load_skins()
        skins.append([
            data['link'],
            str(data['min_float']),
            str(data['max_float']),
            str(percent)
        ])
        save_skins(skins)
        await message.answer(
            f"✅ Скин добавлен!\n"
            f"Ссылка: {data['link']}\n"
            f"Диапазон float: {data['min_float']}-{data['max_float']}\n"
            f"Макс. процент: {percent}%"
        )
        await state.clear()