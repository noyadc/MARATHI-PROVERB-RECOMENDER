import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[0]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.api.main import app
from app.services.verifier import verifier

client = TestClient(app)


@pytest.mark.parametrize('sentence', [
    'आम्ही कष्ट करतो आणि यश मिळवू इच्छितो',
    'मित्रांसोबत एकत्र हसणे आणि आनंद वाटणे',
])
def test_recommend_api_returns_proverbs(sentence):
    response = client.post('/api/recommend', json={'sentence': sentence})
    assert response.status_code == 200
    data = response.json()
    assert 'proverb' in data
    assert 'meaning' in data
    assert 'confidence' in data
    assert isinstance(data['top_matches'], list)
    assert len(data['top_matches']) > 0
    assert data['source'] == 'dataset'
    assert data['verification_status'] == 'verified'


def test_recommend_api_rejects_empty_sentence():
    response = client.post('/api/recommend', json={'sentence': ''})
    assert response.status_code == 400
    assert response.json()['detail'] == 'Sentence is required.'


def test_recommend_api_exact_situation_match():
    sentence = 'अभ्यास न करता परीक्षेला जाणे'
    response = client.post('/api/recommend', json={'sentence': sentence})
    assert response.status_code == 200
    data = response.json()
    assert data['proverb'] == 'घाईचे काम शैतानाचे.'
    assert data['meaning'] == 'कोणतेही काम विचारपूर्वक करावे.'
    assert data['category'] == 'शहाणपण'
    assert data['emotion'] == 'इशारा'
    assert data['confidence'] == 100.0
    assert data['source'] == 'dataset'
    assert data['verification_status'] == 'verified'
    assert data['top_matches'][0]['proverb'] == 'घाईचे काम शैतानाचे.'


def test_verifier_service_accurately_verifies():
    # 1. Dataset proverb
    v1 = verifier.verify("घाईचे काम शैतानाचे.")
    assert v1["is_verified"] is True
    assert v1["verification_status"] == "verified"

    # 2. Curated external traditional proverb
    v2 = verifier.verify("उंटावरून शेळ्या हाकणे")
    assert v2["is_verified"] is True
    assert v2["verification_status"] == "verified"
    assert "मोल्सवर्थ" in v2["source_reference"] or "महाराष्ट्र शब्दकोश" in v2["source_reference"] or "म्हणी" in v2["source_reference"]

    # 3. Made-up non-authentic saying
    v3 = verifier.verify("संगणक चालवताना कॉफी सांडली तर कीबोर्ड खराब होतो")
    assert v3["is_verified"] is False
    assert v3["verification_status"] == "unverified"
    assert "अपुष्टीकृत" in v3["verification_label"] or "Unverified" in v3["verification_label"]


def test_configurable_threshold_activates_fallback_path():
    # When threshold is set artificially high (0.99) for a non-exact sentence,
    # the fallback path is guaranteed to trigger.
    # Without an API key set, it must return closest dataset matches with a fallback notice and no crash.
    sentence = 'आम्ही कष्ट करतो आणि यश मिळवू इच्छितो'
    response = client.post('/api/recommend', json={'sentence': sentence, 'threshold': 0.99})
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'dataset'
    assert data['fallback_notice'] is not None
    assert 'fallback_reason' in data
    assert 'threshold (0.99)' in data['fallback_reason']
    assert len(data['top_matches']) > 0


@patch('app.api.recommendation.get_ai_fallback_recommendation', new_callable=AsyncMock)
def test_ai_fallback_verified_success(mock_ai):
    mock_ai.return_value = {
        'status': 'success',
        'notice': None,
        'data': {
            'proverb': 'उंटावरून शेळ्या हाकणे',
            'meaning': 'प्रत्यक्ष कष्ट न करता लांबूनच केवळ हुकूम सोडणे.',
            'meaning_in_depth': 'स्वतः कामात प्रत्यक्ष सहभागी न होता दुसऱ्याला सूचना देणे.',
            'situation': 'कंपनीचा मॅनेजर स्वतः काम न करता कर्मचाऱ्यांना अवास्तव सूचना देतो.',
            'category': 'कार्यशैली',
            'emotion': 'उपहास',
            'keywords': ['काम', 'हुकूम', 'व्यवस्थापन', 'management'],
            'match_explanation': 'हा प्रसंग केवळ लांबून सल्ला देणाऱ्या व्यवस्थापकांसाठी अगदी योग्य आहे.',
            'verification_status': 'verified',
            'verification_label': 'Verified Traditional Proverb',
            'verification_details': 'पडताळणी यशस्वी: ही म्हण प्रमाणित मराठी संदर्भामध्ये उपलब्ध आहे.',
            'source_reference': 'मराठी म्हणी व त्यांचे अर्थ (महाराष्ट्र शब्दकोश)',
            'source_link': 'https://mr.wikipedia.org/wiki/मराठी_म्हणी',
        }
    }

    # Trigger with threshold 0.99 so fallback is guaranteed
    response = client.post('/api/recommend', json={
        'sentence': 'कंपनीचा बॉस प्रत्यक्ष काम करत नाही पण लांबून सल्ले देतो',
        'threshold': 0.99
    })
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'ai_fallback'
    assert data['source_label'] == 'AI Fallback (OpenAI)'
    assert data['proverb'] == 'उंटावरून शेळ्या हाकणे'
    assert data['verification_status'] == 'verified'
    assert data['confidence'] is None  # Uncalibrated for AI suggestions
    assert data['confidence_label'] is not None
    assert data['match_explanation'] == 'हा प्रसंग केवळ लांबून सल्ला देणाऱ्या व्यवस्थापकांसाठी अगदी योग्य आहे.'
    assert 'tokens' in data['preprocessing']
    assert isinstance(data['top_matches'], list)


@patch('app.api.recommendation.get_ai_fallback_recommendation', new_callable=AsyncMock)
def test_ai_fallback_unverified_suggestion(mock_ai):
    mock_ai.return_value = {
        'status': 'success',
        'notice': None,
        'data': {
            'proverb': 'इंटरनेटच्या जगात पुस्तकांचे महत्त्व कमी झाले',
            'meaning': 'आधुनिक डिजिटल तंत्रज्ञानामुळे वाचन संस्कृती मागे पडली.',
            'meaning_in_depth': 'वाचनाची आवड कमी होणे आणि स्क्रीन टाईम वाढणे.',
            'situation': 'मुले दिवसभर मोबाईलमध्ये असतात.',
            'category': 'तंत्रज्ञान',
            'emotion': 'चिंता',
            'keywords': ['इंटरनेट', 'पुस्तक'],
            'match_explanation': 'आधुनिक स्थितीवर सुचवलेली नवीन म्हण.',
            'verification_status': 'unverified',
            'verification_label': 'Unverified AI Suggestion',
            'verification_details': 'अपुष्टीकृत: ही म्हण आमच्या प्रमाणित पारंपरिक संकलनात थेट आढळली नाही.',
            'source_reference': 'अपुष्टीकृत संदर्भ',
            'source_link': None,
        }
    }

    response = client.post('/api/recommend', json={
        'sentence': 'मुले दिवसभर मोबाईलमध्ये असतात',
        'threshold': 0.99
    })
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'ai_fallback'
    assert data['verification_status'] == 'unverified'
    assert 'Unverified' in data['verification_label']


@patch('app.api.recommendation.get_ai_fallback_recommendation', new_callable=AsyncMock)
def test_ai_fallback_authentic_not_found(mock_ai):
    mock_ai.return_value = {
        'status': 'authentic_proverb_not_found',
        'error_detail': 'No authentic traditional proverb found.',
        'notice': 'या प्रसंगासाठी कोणतीही अस्सल पारंपारिक म्हण उपलब्ध नाही.',
        'data': None,
    }

    response = client.post('/api/recommend', json={
        'sentence': 'क्वांटम कॉम्प्युटर आणि आर्टिफिशियल इंटेलिजन्सचे नवीन अल्गोरिदम',
        'threshold': 0.99
    })
    assert response.status_code == 200
    data = response.json()
    assert data['source'] == 'dataset'
    assert data['verification_status'] == 'not_found'
    assert 'या प्रसंगासाठी कोणतीही अस्सल पारंपारिक म्हण उपलब्ध नाही' in data['fallback_notice']
    assert len(data['top_matches']) > 0
