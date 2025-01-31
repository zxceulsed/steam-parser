import requests
import json

def clean_inspect_link(link: str) -> str:
    """Очистка инспекционной ссылки"""
    return link.replace("%20", " ").replace(" 20M", " M").strip()

def get_swapgg_float(inspect_link: str) -> float:
    """Получение float через Swap.gg API"""
    headers = {
        'authority': 'api.swap.gg',
        'accept': 'application/json',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.post(
            "https://api.swap.gg/v2/screenshot",
            headers=headers,
            json={"inspectLink": clean_inspect_link(inspect_link)},
            timeout=15
        )
        return float(response.json().get('result', {}).get('meta', {}).get('16', {}).get('o', 0.0))
    except:
        return 0.0