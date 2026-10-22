import logging
from fastapi import APIRouter, HTTPException
from ..schemas.proverb import RecommendationRequest, RecommendationResponse
from ..recommendation.engine import engine
from ..services.ai_fallback import get_ai_fallback_recommendation
from ..services.verifier import verifier

router = APIRouter()
logger = logging.getLogger("recommendation")


@router.post('', response_model=RecommendationResponse)
async def recommend_proverb(request: RecommendationRequest):
    sentence = request.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail='Sentence is required.')

    # Step 1: Search Existing Dataset using LaBSE embeddings & exact-match override
    dataset_res = engine.search_dataset(sentence, top_k=5, threshold=request.threshold)
    top_matches = dataset_res['top_matches']
    is_exact_match = dataset_res['is_exact_match']
    best_similarity = dataset_res['best_similarity']
    meets_threshold = dataset_res['meets_threshold']
    threshold_used = dataset_res['threshold_used']
    query_preprocessing = dataset_res['query_preprocessing']

    if not top_matches:
        raise HTTPException(status_code=404, detail='No recommendation found.')

    best_dataset_match = top_matches[0]

    # Step 2: Determine Whether the Match Is Relevant
    # If exact match exists or best similarity score meets threshold: return dataset recommendation
    if is_exact_match or meets_threshold:
        return {
            'proverb': best_dataset_match['proverb'],
            'meaning': best_dataset_match['meaning'],
            'meaning_in_depth': best_dataset_match.get('meaning_in_depth'),
            'situation': best_dataset_match['situation'],
            'category': best_dataset_match['category'],
            'keywords': best_dataset_match['keywords'],
            'emotion': best_dataset_match['emotion'],
            'confidence': min(best_dataset_match['confidence'], 100.0),
            'confidence_label': f"{best_dataset_match['confidence']:.1f}%",
            'source': 'dataset',
            'source_label': 'Traditional Collection',
            'verification_status': 'verified',
            'verification_label': 'Verified Traditional Proverb',
            'verification_details': 'पारंपरिक मराठी साहित्यातील प्रमाणित म्हण.',
            'source_reference': 'पारंपरिक मराठी म्हणी संग्रह',
            'source_link': 'https://mr.wikipedia.org/wiki/मराठी_म्हणी',
            'match_explanation': 'दिलेले वाक्य पारंपारिक प्रसंग व परिस्थितीशी तंतोतंत सुसंगत आढळले.',
            'fallback_reason': None,
            'fallback_notice': None,
            'threshold_used': threshold_used,
            'similarity_score': best_similarity,
            'top_matches': top_matches,
            'preprocessing': best_dataset_match.get('preprocessing') or query_preprocessing,
        }

    # Step 3: Activate AI Fallback using OpenAI API
    fallback_reason = (
        f"Dataset similarity ({best_similarity:.2f}) is below threshold ({threshold_used:.2f}). "
        f"AI Fallback activated."
    )
    logger.info(fallback_reason)

    ai_result = await get_ai_fallback_recommendation(sentence)

    # Step 4: Verify and Handle AI Fallback Result
    if ai_result["status"] == "success" and ai_result.get("data"):
        data = ai_result["data"]
        ai_proverb = data["proverb"]

        # Ensure no duplicate proverbs appear in top_matches
        filtered_top_matches = [
            m for m in top_matches if not verifier.is_duplicate(m["proverb"], ai_proverb)
        ]

        # Generate preprocessing breakdown for the AI recommended proverb
        ai_preprocessing = engine.preprocess_text(ai_proverb)

        return {
            'proverb': ai_proverb,
            'meaning': data['meaning'],
            'meaning_in_depth': data.get('meaning_in_depth'),
            'situation': data.get('situation') or sentence,
            'category': data.get('category') or 'सामान्य',
            'keywords': data.get('keywords') or [],
            'emotion': data.get('emotion') or 'बोध',
            'confidence': None,  # Explicitly do not treat AI estimate as calibrated probability
            'confidence_label': 'AI Relevance Suggestion (Uncalibrated)',
            'source': 'ai_fallback',
            'source_label': 'AI Fallback (OpenAI)',
            'verification_status': data['verification_status'],
            'verification_label': data['verification_label'],
            'verification_details': data['verification_details'],
            'source_reference': data['source_reference'],
            'source_link': data.get('source_link'),
            'match_explanation': data.get('match_explanation') or 'AI मॉडेलने या परिस्थितीसाठी ही म्हण सुचवली आहे.',
            'fallback_reason': fallback_reason,
            'fallback_notice': None,
            'threshold_used': threshold_used,
            'similarity_score': best_similarity,
            'top_matches': filtered_top_matches,
            'preprocessing': ai_preprocessing,
        }

    # If AI could not identify an authentic proverb, or if fallback failed (rate limit, timeout, missing key)
    # Display the closest dataset matches with an appropriate notice
    notice = ai_result.get("notice") or "स्थानिक डेटासेटमधील सर्वात जवळचे पर्याय दर्शविले आहेत."
    return {
        'proverb': best_dataset_match['proverb'],
        'meaning': best_dataset_match['meaning'],
        'meaning_in_depth': best_dataset_match.get('meaning_in_depth'),
        'situation': best_dataset_match['situation'],
        'category': best_dataset_match['category'],
        'keywords': best_dataset_match['keywords'],
        'emotion': best_dataset_match['emotion'],
        'confidence': min(best_dataset_match['confidence'], 100.0),
        'confidence_label': f"{best_dataset_match['confidence']:.1f}%",
        'source': 'dataset',
        'source_label': 'Traditional Collection',
        'verification_status': 'verified' if ai_result["status"] != "authentic_proverb_not_found" else 'not_found',
        'verification_label': (
            'No Authentic Proverb Found (Showing Closest Match)'
            if ai_result["status"] == "authentic_proverb_not_found"
            else 'Verified Traditional Proverb'
        ),
        'verification_details': (
            'AI मॉडेलने पुष्टी केली की या प्रसंगासाठी कोणतीही अस्सल पारंपारिक म्हण उपलब्ध नाही. त्यामुळे पारंपारिक म्हणी संग्रहातील सर्वात जवळचा पर्याय निवडला आहे.'
            if ai_result["status"] == "authentic_proverb_not_found"
            else 'पारंपरिक म्हणी संग्रहातील सर्वात समर्पक पर्याय.'
        ),
        'source_reference': 'पारंपरिक मराठी म्हणी संग्रह',
        'source_link': 'https://mr.wikipedia.org/wiki/मराठी_म्हणी',
        'match_explanation': "दिलेल्या प्रसंगासाठी सर्वात समर्पक पारंपारिक म्हण निवडण्यात आली आहे.",
        'fallback_reason': fallback_reason,
        'fallback_notice': notice,
        'threshold_used': threshold_used,
        'similarity_score': best_similarity,
        'top_matches': top_matches,
        'preprocessing': best_dataset_match.get('preprocessing') or query_preprocessing,
    }
