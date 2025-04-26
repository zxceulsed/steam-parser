import requests
import time
from bs4 import BeautifulSoup
from services.float_parser import get_swapgg_float
from parsing.cookies import get_steam_cookies
from utils.validation import parse_price

async def process_market_url(url: str, target_min: float, target_max: float, max_percent: float) -> str:
    json_url = url.rstrip("/")
    if "/render/" not in json_url:
        json_url = f"{json_url}/render/?query=&start=0&count=100&country=RU&language=english&currency=5"
    response = requests.get(
        json_url,
        cookies=get_steam_cookies(),
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    if response.status_code != 200:
        return f"Ошибка: Steam вернул код {response.status_code}"
    data = response.json()
    html_results = data.get("results_html", "")
    soup = BeautifulSoup(html_results, 'html.parser')
    title_element = soup.find('div', class_='market_listing_nav')
    title = title_element.text.strip() if title_element else "Неизвестный предмет"
    items = soup.select('div.market_listing_row')
    if not items:
        return ""
    first_price_str = items[0].select_one('.market_listing_price_with_fee').text.strip()
    base_price = parse_price(first_price_str)
    found = []
    for idx, item in enumerate(items):
        price_el = item.select_one('.market_listing_price_with_fee')
        price_str = price_el.text.strip() if price_el else ""
        current_price = parse_price(price_str)
        if current_price <= 0:
            continue
        diff = 0.0 if idx == 0 else ((current_price - base_price) / base_price) * 100
        if idx != 0 and diff > max_percent:
            continue
        link = item.select_one('a[href^="steam://"]')['href']
        flt = get_swapgg_float(link)
        if target_min <= flt <= target_max:
            found.append({
                'title': title,
                'price': current_price,
                'float': flt,
                'diff': diff,
                'url': url
            })
        time.sleep(1)
    if not found:
        return ""
    return '\n\n'.join([
        f"🎉 Найден {f['title']} — {f['price']:.2f} руб, float {f['float']:.8f}, diff {f['diff']:.1f}% — {f['url']}"
        for f in found
    ])