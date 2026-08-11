import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[0]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.api.main import app

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
    assert data['top_matches'][0]['proverb'] == 'घाईचे काम शैतानाचे.'
