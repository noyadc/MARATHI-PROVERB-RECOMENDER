from fastapi import APIRouter, HTTPException
from ..schemas.proverb import RecommendationRequest, RecommendationResponse
from ..recommendation.engine import engine

router = APIRouter()

@router.post('', response_model=RecommendationResponse)
async def recommend_proverb(request: RecommendationRequest):
    if not request.sentence.strip():
        raise HTTPException(status_code=400, detail='Sentence is required.')

    matches = engine.recommend(request.sentence)
    if not matches:
        raise HTTPException(status_code=404, detail='No recommendation found.')

    best = matches[0]
    return {
        'proverb': best['proverb'],
        'meaning': best['meaning'],
        'meaning_in_depth': best.get('meaning_in_depth'),
        'situation': best['situation'],
        'category': best['category'],
        'keywords': best['keywords'],
        'emotion': best['emotion'],
        'confidence': min(best['confidence'], 100.0),
        'preprocessing': best.get('preprocessing'),
        'top_matches': matches,
    }
