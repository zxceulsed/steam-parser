from typing import List

def parse_price(s: str) -> float:
    s = s.strip().replace(' ', '').replace('руб.', '').replace('$', '').replace(',', '.')
    s = ''.join([c for c in s if c.isdigit() or c == '.'])
    try:
        return float(s)
    except ValueError:
        return 0.0

def validate_cookies(data: List[dict]) -> bool:
    req = {'name', 'value', 'domain'}
    return all(req.issubset(cookie.keys()) for cookie in data)