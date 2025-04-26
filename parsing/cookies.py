import json
from pathlib import Path

def get_steam_cookies() -> dict:
    path = Path('cookies.json')
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    return {c['name']: c['value'] for c in data if 'name' in c and 'value' in c}