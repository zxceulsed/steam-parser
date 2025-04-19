import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboard import main_menu, back_menu
from steam_parser import process_market_url, get_steam_cookies
import json

class Form(StatesGroup):
    waiting_link = State()
    waiting_float = State()
    waiting_percent = State()
    waiting_delete = State()
    waiting_cookies = State()
    
bot = Bot(token="5850044952:AAG8m316opUqrEDrbmRhOrg4kieHUZ-WwjE")
dp = Dispatcher()
monitoring_active = False

def load_skins():
    if not os.path.exists('links.txt'):
        return []
    with open('links.txt', 'r', encoding='utf-8') as f:
        return [line.strip().split('~|~') for line in f.readlines()]


def save_skins(skins):
    with open('links.txt', 'w', encoding='utf-8') as f:
        for skin in skins:
            f.write('~|~'.join(skin) + '\n')

def validate_cookies(data: list) -> bool:
    required_fields = {'name', 'value', 'domain'}
    for cookie in data:
        if not all(field in cookie for field in required_fields):
            return False
    return True

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
        
        await state.update_data(min_float=min_float, max_float=max_float)
        await state.set_state(Form.waiting_percent)
        await message.answer(
            "Введите максимальный допустимый процент превышения цены (например 20):",
            reply_markup=back_menu()
        )
        
    except ValueError:
        await message.answer("❌ Неверный формат диапазона! Используйте пример: 0.00-0.02")

@dp.message(Form.waiting_percent)
async def process_percent(message: Message, state: FSMContext):
    try:
        percent = float(message.text)
        if percent <= 0:
            return await message.answer("❌ Процент должен быть положительным числом!")
        
        data = await state.get_data()
        skins = load_skins()
        skins.append([data['link'], str(data['min_float']), str(data['max_float']), str(percent)])
        save_skins(skins)
        
        await message.answer(
            f"✅ Скин успешно добавлен!\n"
            f"Ссылка: {data['link']}\n"
            f"Диапазон float: {data['min_float']}-{data['max_float']}\n"
            f"Макс. превышение цены: {percent}%",
            reply_markup=main_menu()
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Введите корректное числовое значение!")

@dp.message(F.text == 'Удалить скин')
async def delete_skin(message: Message, state: FSMContext):
    skins = load_skins()
    if not skins:
        return await message.answer("📂 Список скинов пуст!")
    
    response = ["🗑 Список скинов для удаления:"]
    for i, (link, min_float, max_float, percent) in enumerate(skins, 1):
        response.append(f"{i}. {link}\nДиапазон: {min_float}-{max_float}\nПроцент: {percent}%")
    
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
    for i, (link, min_float, max_float, percent) in enumerate(skins, 1):
        response.append(f"{i}. {link}\nДиапазон float: {min_float}-{max_float}\nМакс. процент: {percent}%")
    
    await message.answer('\n'.join(response))

@dp.message(F.text == 'Начать мониторинг')
async def start_monitoring(message: Message):
    global monitoring_active
    
    # Проверка наличия куки
    cookies = get_steam_cookies()
    if not cookies:
        return await message.answer("❌ Сначала обновите куки через меню!")
    
    monitoring_active = True
    await message.answer("🔍 Начинаем мониторинг скинов... (проверка каждые 5 минут)")
    asyncio.create_task(check_skins_periodically(message))

async def check_skins_periodically(message: Message):
    global monitoring_active
    while monitoring_active:
        skins = load_skins()
        for skin_entry in skins:
            # Распаковываем 4 значения вместо 3
            url, min_float, max_float, max_percent = skin_entry
            result = await process_market_url(
                url, 
                float(min_float), 
                float(max_float),
                float(max_percent)  # Добавляем процент в вызов
            )
            if result:
                await message.answer(f"🎉 Найден подходящий скин!\n{result}")
        await asyncio.sleep(300)

@dp.message(F.text == 'Назад в меню')
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu())

@dp.message(F.text == 'Обновить куки')
async def update_cookies(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_cookies)
    await message.answer("Отправьте файл cookies.json с обновленными куками:", reply_markup=back_menu())

@dp.message(Form.waiting_cookies, F.document)
async def handle_cookies_file(message: Message, state: FSMContext):
    try:
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, destination="cookies.json")
        
        # Проверка валидности JSON
        with open("cookies.json", 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)  # Теперь json импортирован
            
            if not validate_cookies(cookies_data):
                raise ValueError("Некорректный формат файла")
        
        await message.answer("✅ Куки успешно обновлены!", reply_markup=main_menu())
        
    except json.JSONDecodeError:  # Обработка ошибок JSON
        await message.answer("❌ Файл поврежден или не является JSON!", reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=main_menu())
    finally:
        await state.clear()


if __name__ == '__main__':
    dp.run_polling(bot)