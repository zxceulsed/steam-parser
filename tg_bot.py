import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboard import main_menu, back_menu
from steam_parser import process_market_url

class Form(StatesGroup):
    waiting_link = State()
    waiting_float = State()
    waiting_delete = State()

bot = Bot(token="7697546458:AAFslu4K6V2DPG-k0jkw9ThYV-8j2Iy8z7E")
dp = Dispatcher()
monitoring_active = False

def load_skins():
    if not os.path.exists('links.txt'):
        return []
    with open('links.txt', 'r', encoding='utf-8') as f:
        return [line.strip().split('|') for line in f.readlines()]

def save_skins(skins):
    with open('links.txt', 'w', encoding='utf-8') as f:
        for skin in skins:
            f.write('|'.join(skin) + '\n')

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🏷️ Бот для мониторинга скинов CS2\nВыберите действие:",
        reply_markup=main_menu()
    )

@dp.message(F.text == 'Добавить скин')
async def add_skin(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_link)
    await message.answer(
        "Отправьте ссылку на страницу скина с Steam Market:",
        reply_markup=back_menu()
    )

@dp.message(Form.waiting_link)
async def process_link(message: Message, state: FSMContext):
    if 'назад' in message.text.lower():
        await state.clear()
        return await message.answer("Главное меню:", reply_markup=main_menu())
    
    if not message.text.startswith('https://steamcommunity.com/market'):
        return await message.answer("❌ Это не похоже на Steam Market ссылку!")
    
    await state.update_data(link=message.text)
    await state.set_state(Form.waiting_float)
    await message.answer(
        "Теперь отправьте диапазон float в формате:\n0.00-0.02",
        reply_markup=back_menu()
    )

@dp.message(Form.waiting_float)
async def process_float(message: Message, state: FSMContext):
    if 'назад' in message.text.lower():
        await state.clear()
        return await message.answer("Главное меню:", reply_markup=main_menu())
    
    try:
        min_float, max_float = map(float, message.text.split('-'))
        if min_float > max_float:
            return await message.answer("❌ Минимальное значение должно быть меньше максимального!")
        
        data = await state.get_data()
        skins = load_skins()
        skins.append([data['link'], str(min_float), str(max_float)])
        save_skins(skins)
        
        await message.answer(
            f"✅ Скин успешно добавлен!\n"
            f"Ссылка: {data['link']}\n"
            f"Диапазон float: {min_float}-{max_float}",
            reply_markup=main_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат диапазона! Используйте пример: 0.00-0.02")

@dp.message(F.text == 'Удалить скин')
async def delete_skin(message: Message, state: FSMContext):
    skins = load_skins()
    if not skins:
        return await message.answer("📂 Список скинов пуст!")
    
    response = ["🗑 Список скинов для удаления:"]
    for i, (link, min_float, max_float) in enumerate(skins, 1):
        response.append(f"{i}. {link}\nДиапазон: {min_float}-{max_float}")
    
    await state.set_state(Form.waiting_delete)
    await message.answer('\n'.join(response) + "\n\nВведите номер скина для удаления:", reply_markup=back_menu())

@dp.message(Form.waiting_delete)
async def process_delete(message: Message, state: FSMContext):
    if 'назад' in message.text.lower():
        await state.clear()
        return await message.answer("Главное меню:", reply_markup=main_menu())
    
    try:
        index = int(message.text) - 1
        skins = load_skins()
        
        if 0 <= index < len(skins):
            deleted_skin = skins.pop(index)
            save_skins(skins)
            await message.answer(
                f"✅ Скин успешно удален:\n"
                f"{deleted_skin[0]}\n"
                f"Диапазон: {deleted_skin[1]}-{deleted_skin[2]}",
                reply_markup=main_menu()
            )
        else:
            await message.answer("❌ Неверный номер скина!", reply_markup=main_menu())
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Введите корректный номер!", reply_markup=main_menu())

@dp.message(F.text == 'Просмотреть скины')
async def view_skins(message: Message):
    skins = load_skins()
    if not skins:
        return await message.answer("📂 Список скинов пуст")
    
    response = ["📋 Список отслеживаемых скинов:"]
    for i, (link, min_float, max_float) in enumerate(skins, 1):
        response.append(f"{i}. {link}\nДиапазон float: {min_float}-{max_float}")
    
    await message.answer('\n'.join(response))

@dp.message(F.text == 'Начать мониторинг')
async def start_monitoring(message: Message):
    global monitoring_active
    monitoring_active = True
    await message.answer("🔍 Начинаем мониторинг скинов... (проверка каждые 5 минут)")
    asyncio.create_task(check_skins_periodically(message))

async def check_skins_periodically(message: Message):
    global monitoring_active
    while monitoring_active:
        skins = load_skins()
        for url, min_float, max_float in skins:
            result = await process_market_url(url, float(min_float), float(max_float))
            if result:
                await message.answer(f"🎉 Найден подходящий скин!\n{result}")
        await asyncio.sleep(300)

@dp.message(F.text == 'Назад в меню')
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu())

if __name__ == '__main__':
    dp.run_polling(bot)