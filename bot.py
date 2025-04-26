import asyncio
import sys
import os
# Добавляем src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from config import settings
from aiogram import Bot, Dispatcher
from handlers import register_all_handlers

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    register_all_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())