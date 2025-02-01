from bs4 import BeautifulSoup
import requests
import time
import json
from pathlib import Path
from float_parser import get_swapgg_float

def get_steam_cookies():
    """Загружает куки из файла или возвращает дефолтные"""
    cookie_file = Path("cookies.json")
    cookies = {}
    
    try:
        if cookie_file.exists():
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
                cookies = {c['name']: c['value'] for c in cookies_data}
        else:
            print("Отправьте файл куки")
    except Exception as e:
        print(f"Ошибка загрузки куки: {e}")
    
    return cookies

def build_json_url(url: str) -> str:
    """
    Преобразует исходную ссылку в ссылку для получения JSON с 100 позициями.
    Если в ссылке уже присутствует '/render/', она не изменяется.
    """
    if "/render/" in url:
        return url
    url = url.rstrip("/")  # убираем завершающий слеш, если есть
    json_url = (
        f"{url}/render/"
        f"?query=&start=0&count=100&country=RU&language=english&currency=5"
    )
    return json_url


def parse_price(price_str: str) -> float:
    """Парсит цену из строки с любым форматом валюты"""
    # Удаляем все нечисловые символы, кроме точек и запятых
    clean_str = (
        price_str.strip()
        .replace(" ", "")      # Убираем пробелы
        .replace("руб.", "")   # Удаляем обозначение рублей
        .replace("$", "")      # Удаляем доллары
        .replace(",", ".")     # Заменяем запятые на точки
    )
    
    # Оставляем только цифры и точку
    clean_str = "".join([c for c in clean_str if c.isdigit() or c == "."])
    
    try:
        return float(clean_str)
    except ValueError:
        return 0.0  # Возвращаем 0 в случае ошибки

async def process_market_url(url: str, target_min: float, target_max: float, max_percent: float) -> str:
    try:
        # Формируем URL для JSON-запроса
        json_url = build_json_url(url)
        
        # Отправляем запрос к Steam
        response = requests.get(
            json_url,
            cookies=get_steam_cookies(),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            },
            timeout=15
        )
        
        if response.status_code != 200:
            return f"Ошибка: Steam вернул код {response.status_code}"
        
        # Парсим результаты
        data = response.json()
        html_results = data.get("results_html", "")
        
        # Создаем объект BeautifulSoup в любом случае
        soup = BeautifulSoup(html_results, 'html.parser')
        
        # Получаем название скина
        title_element = soup.find('div', class_='market_listing_nav')
        title = title_element.text.strip() if title_element else "Неизвестный предмет"
        
        # Получаем все элементы списка
        items = soup.select('div.market_listing_row')
        if not items:
            return ""
        
        # Базовая цена (первый элемент в списке)
        first_price_str = items[0].select_one('.market_listing_price_with_fee').text.strip()
        base_price = parse_price(first_price_str)
        
        found_items = []
        
        # Проверяем все элементы
        for index, item in enumerate(items):
            try:
                # Парсим цену
                price_element = item.select_one('.market_listing_price_with_fee')
                price_str = price_element.text.strip() if price_element else "N/A"
                if price_str == "N/A":
                    continue
                
                current_price = parse_price(price_str)
                if current_price <= 0:
                    continue
                
                # Рассчитываем разницу в цене
                price_diff_percent = 0.0 if index == 0 else ((current_price - base_price) / base_price) * 100
                
                # Проверяем превышение процента (кроме первого элемента)
                if index != 0 and price_diff_percent > max_percent:
                    continue
                
                # Получаем float
                inspect_link = item.select_one('a[href^="steam://"]')['href']
                float_value = get_swapgg_float(inspect_link)
                
                # Проверяем диапазон float
                if target_min <= float_value <= target_max:
                    found_items.append({
                        'title': title,
                        'price': current_price,
                        'float': float_value,
                        'price_diff': price_diff_percent,
                        'url': url
                    })
                
                time.sleep(1)  # Задержка между запросами
                
            except Exception as inner_e:
                print(f"Ошибка обработки элемента: {inner_e}")
                continue

        # Формируем результат
        if found_items:
            return '\n\n'.join([
                f"🎉 Найден подходящий скин!\n"
                f"🏷 Название: {item['title']}\n"
                f"💰 Цена: {item['price']:.2f} руб.\n"
                f"🎚 Float: {item['float']:.8f}\n"
                f"📈 Отличие от базовой цены: {item['price_diff']:.1f}%\n"
                f"🔗 Ссылка: {item['url']}"
                for item in found_items
            ])
        return ""
    
    except Exception as e:
        return f"Ошибка обработки страницы: {str(e)}"