from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user_states import Form
from keyboards.reply import back_menu
from services.storage import load_skins, save_skins


def register_delete_skin_handlers(dp: Dispatcher):
    @dp.message(F.text == "Удалить скин")
    async def delete_skin(message: Message, state: FSMContext):
        skins = load_skins()
        if not skins:
            await message.answer("📂 Список скинов пуст!")
            return
        lines = [
            f"{i+1}. {link} — float {min_f}-{max_f}, % {pct}%"
            for i, (link, min_f, max_f, pct) in enumerate(skins)
        ]
        await state.set_state(Form.waiting_delete)
        await message.answer(
            "🗑 Выберите номер скина для удаления:\n" + "\n".join(lines),
            reply_markup=back_menu()
        )

    @dp.message(Form.waiting_delete)
    async def process_delete(message: Message, state: FSMContext):
        text = message.text.strip()
        try:
            idx = int(text) - 1
        except:
            await message.answer("❌ Введите номер из списка!")
            return
        skins = load_skins()
        if 0 <= idx < len(skins):
            deleted = skins.pop(idx)
            save_skins(skins)
            await message.answer(
                f"✅ Скин удалён:\n{deleted[0]} — float {deleted[1]}-{deleted[2]}"
            )
        else:
            await message.answer("❌ Неверный номер!")
        await state.clear()