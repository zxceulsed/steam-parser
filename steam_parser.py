from bs4 import BeautifulSoup
import requests
import time
from float_parser import get_swapgg_float

def get_steam_cookies():
    """Возвращает актуальные куки для Steam Community"""
    return {
        "steamCountry": "DE%7Cdf1227bcafad6a1278d31b61162fe5f7",
        "browserid": "1790214141277757",
        "sessionid": "97224f28e4c995a116b229c0",
        "steamDidLoginRefresh": "1738262876",
        "steamLoginSecure": "76561198894921863%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MDAwRF8yNUMzMEI2Ml81QUJDNCIsICJzdWIiOiAiNzY1NjExOTg4OTQ5MjE4NjMiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3MzgzNTg5MzcsICJuYmYiOiAxNzI5NjMxODA3LCAiaWF0IjogMTczODI3MTgwNywgImp0aSI6ICIwMDBCXzI1QzMwQjc0Xzg1OTExIiwgIm9hdCI6IDE3MzgxNzQzNDIsICJydF9leHAiOiAxNzU2MDEwNzM2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMzcuMjE1LjQyLjE1NCIsICJpcF9jb25maXJtZXIiOiAiMzcuMjE1LjQyLjE1NCIgfQ.YGEVXOFcUvD6Jnk0tjOfK86fDA-fHdTTneDwH43xpOdlJk8voDu0VFT-h-PdBUFk8QrhOciUuY29j386bmQaDg",
        "timezoneOffset": "10800,0",
        "webTradeEligibility": "%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22%3A1738271809%7D"
    }

async def process_market_url(url: str, target_min: float, target_max: float) -> str:
    """Парсит страницу маркета Steam с использованием куки"""
    try:
        # Запрос с куками и заголовками
        response = requests.get(
            url,
            cookies=get_steam_cookies(),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            },
            timeout=15
        )
        
        # Проверка на успешный ответ
        if response.status_code != 200:
            return f"Ошибка: Steam вернул код {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Парсинг названия
        title_element = soup.find('div', class_='market_listing_nav')
        title = title_element.text.strip() if title_element else "Неизвестный предмет"
        
        # Поиск предложений
        items = soup.select('div.market_listing_row')[:10]
        found_items = []
        
        for idx, item in enumerate(items, 1):
            try:
                # Извлечение данных
                price_element = item.select_one('.market_listing_price_with_fee')
                price = price_element.text.strip() if price_element else "N/A"
                
                inspect_link_element = item.select_one('a[href^="steam://"]')
                if not inspect_link_element:
                    continue
                    
                inspect_link = inspect_link_element['href']
                float_value = get_swapgg_float(inspect_link)
                
                # Проверка диапазона float
                if target_min <= float_value <= target_max:
                    found_items.append({
                        'title': title,
                        'price': price,
                        'float': float_value,
                        'url': url
                    })
                
                time.sleep(1)  # Анти-флуд
                
            except Exception as e:
                continue

        # Формирование результата
        if found_items:
            result = []
            for item in found_items:
                result.append(
                    f"🏷 {item['title']}\n"
                    f"💰 Цена: {item['price']}\n"
                    f"🎚 Float: {item['float']:.8f}\n"
                    f"🔗 Ссылка: {item['url']}"
                )
            return '\n\n'.join(result)
        return ""
    
    except Exception as e:
        return f"Ошибка обработки страницы: {str(e)}"