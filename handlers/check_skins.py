from aiogram import Dispatcher, F
from aiogram.types import Message
from parsing.steam_market import process_market_url
from services.storage import load_skins
from parsing.cookies import get_steam_cookies

def register_check_skins_handlers(dp: Dispatcher):
    @dp.message(F.text == "Просмотреть скины")
    async def check_skins(message: Message):
        skins = load_skins()
        if not skins:
            await message.answer("📂 Список скинов пуст")
            return
        lines = [
            f"{i+1}. {link} — float {min_f}-{max_f}, % {pct}%"
            for i, (link, min_f, max_f, pct) in enumerate(skins)
        ]
        await message.answer("📋 Текущие скины: " + " ".join(lines))