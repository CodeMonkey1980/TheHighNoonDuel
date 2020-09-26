import json
from pathlib import Path


def load_highscore_data():
    path = Path('highscore.json')
    if path.exists():
        return json.loads(path.read_text())
    return {
        'quickest_draw': None,
        'hero': {'wins': 0, 'loses': 0},
        'outlaw': {'wins': 0, 'loses': 0},
        'draws': 0
    }


def save_highscore_data(data):
    with open('highscore.json', 'w+') as f:
        f.write(json.dumps(data))
