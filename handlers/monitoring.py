import asyncio
from aiogram import Dispatcher, F
from aiogram.types import Message
from parsing.steam_market import process_market_url
from services.storage import load_skins
from parsing.cookies import get_steam_cookies

monitoring_active = False


def register_monitoring_handlers(dp: Dispatcher):
    @dp.message(F.text == "Начать мониторинг")
    async def start_monitoring(message: Message):
        global monitoring_active
        cookies = get_steam_cookies()
        if not cookies:
            await message.answer("❌ Сначала обновите куки через меню!")
            return
        monitoring_active = True
        await message.answer("🔍 Мониторинг запущен. Каждые 5 минут будет проверка.")
        asyncio.create_task(check_skins_periodically(message))

async def check_skins_periodically(message: Message):
    while monitoring_active:
        skins = load_skins()
        for url, min_f, max_f, pct in skins:
            result = await process_market_url(
                url,
                float(min_f),
                float(max_f),
                float(pct)
            )
            if result:
                await message.answer(result)
        await asyncio.sleep(300)
