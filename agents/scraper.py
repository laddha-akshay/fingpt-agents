import json
from pathlib import Path

def load_sample_news(path='sample_data/news_sample.jsonl'):
    p = Path(path)
    if not p.exists():
        return []
    items = []
    with p.open('r', encoding='utf-8') as f:
        for line in f:
            items.append(json.loads(line))
    return items
