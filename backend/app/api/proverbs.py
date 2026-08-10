from fastapi import APIRouter, HTTPException
from ..schemas.proverb import ProverbResponse
import csv
from pathlib import Path

router = APIRouter()
DATA_FILE = Path(__file__).resolve().parents[3] / 'dataset' / 'marathi_proverbs_200.csv'

@router.get('', response_model=list[ProverbResponse])
async def list_proverbs():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [
            {
                'id': row['ID'],
                'proverb': row['Proverb'],
                'meaning': row['Meaning'],
                'situation': row['Situation'],
                'category': row['Category'],
                'keywords': row['Keywords'].split(','),
                'emotion': row['Emotion'],
            }
            for row in reader
        ]

@router.get('/{proverb_id}', response_model=ProverbResponse)
async def get_proverb(proverb_id: int):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['ID']) == proverb_id:
                return {
                    'id': row['ID'],
                    'proverb': row['Proverb'],
                    'meaning': row['Meaning'],
                    'situation': row['Situation'],
                    'category': row['Category'],
                    'keywords': row['Keywords'].split(','),
                    'emotion': row['Emotion'],
                }
    raise HTTPException(status_code=404, detail='Proverb not found')
