from fastapi import APIRouter
import csv
from pathlib import Path
from collections import Counter

router = APIRouter()
DATA_FILE = Path(__file__).resolve().parents[3] / 'dataset' / 'marathi_proverbs_200.csv'

@router.get('/summary')
async def analytics_summary():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    categories = dict(Counter(row['Category'] for row in rows))
    emotions = dict(Counter(row['Emotion'] for row in rows))
    return {
        'total_proverbs': len(rows),
        'categories': categories,
        'emotions': emotions,
    }
