from bs4 import BeautifulSoup
import requests
import time
from float_parser import get_swapgg_float

async def process_market_url(url: str, target_min: float, target_max: float) -> str:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('div', class_='market_listing_nav').text.strip()
        items = soup.select('div.market_listing_row')[:10]
        
        found_items = []
        
        for idx, item in enumerate(items, 1):
            try:
                price = item.select_one('.market_listing_price_with_fee').text.strip()
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