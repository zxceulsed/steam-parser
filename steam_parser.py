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
            with open(cookie_file, 'r') as f:
                cookies_data = json.load(f)
                cookies = {c['name']: c['value'] for c in cookies_data}
        else:
            print("Отправьте файл куки")
    except Exception as e:
        print(f"Ошибка загрузки куки: {e}")
    
    return cookies

async def process_market_url(url: str, target_min: float, target_max: float) -> str:
    try:
        response = requests.get(
            url,
            cookies=get_steam_cookies(),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            },
            timeout=15
        )
        
        if response.status_code != 200:
            return f"Ошибка: Steam вернул код {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')
        title_element = soup.find('div', class_='market_listing_nav')
        title = title_element.text.strip() if title_element else "Неизвестный предмет"
        items = soup.select('div.market_listing_row')[:10]
        found_items = []
        
        for item in items:
            try:
                price_element = item.select_one('.market_listing_price_with_fee')
                price = price_element.text.strip() if price_element else "N/A"
                inspect_link = item.select_one('a[href^="steam://"]')['href']
                float_value = get_swapgg_float(inspect_link)
                
                if target_min <= float_value <= target_max:
                    found_items.append({
                        'title': title,
                        'price': price,
                        'float': float_value,
                        'url': url
                    })
                
                time.sleep(1)
            except:
                continue

        if found_items:
            return '\n\n'.join([
                f"🏷 {item['title']}\n💰 Цена: {item['price']}\n🎚 Float: {item['float']:.8f}\n🔗 Ссылка: {item['url']}"
                for item in found_items
            ])
        return ""
    
    except Exception as e:
        return f"Ошибка обработки страницы: {str(e)}"