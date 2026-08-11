import csv
import json
import re
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[3]
PROVERB_FILE = BASE_DIR / 'dataset' / 'marathi_proverbs_200.csv'
EMBEDDINGS_DIR = Path(__file__).resolve().parents[2] / 'embeddings'
PROVERB_EMBEDDINGS_FILE = EMBEDDINGS_DIR / 'proverb_embeddings.npy'
SITUATION_EMBEDDINGS_FILE = EMBEDDINGS_DIR / 'situation_embeddings.npy'
MODEL_NAME = 'sentence-transformers/LaBSE'

class RecommendationEngine:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.proverbs = self._load_proverbs()
        self.lemma_dict = self._load_lemma_dictionary()
        self.proverb_embeddings, self.situation_embeddings = self._load_or_build_embeddings()

    def _load_proverbs(self):
        proverbs = []
        with open(PROVERB_FILE, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                keywords = row.get('Keywords', '') or row.get('keywords', '') or ''
                if isinstance(keywords, str):
                    keywords = [kw.strip().strip('"').strip("'") for kw in keywords.split(',') if kw.strip()]
                proverbs.append({
                    'id': (row.get('ID') or row.get('Id') or row.get('id') or '').strip(),
                    'proverb': (row.get('Proverb') or row.get('proverb') or '').strip(),
                    'meaning': (row.get('Meaning') or row.get('meaning') or '').strip(),
                    'situation': (row.get('Situation') or row.get('situation') or '').strip(),
                    'category': (row.get('Category') or row.get('category') or '').strip(),
                    'keywords': [kw for kw in keywords if kw],
                    'emotion': (row.get('Emotion') or row.get('emotion') or '').strip(),
                })
        return proverbs

    def _load_lemma_dictionary(self):
        lemma_file = BASE_DIR / 'preprocessing' / 'lemma_dictionary.json'
        if lemma_file.exists():
            try:
                with open(lemma_file, 'r', encoding='utf-8') as fh:
                    return json.load(fh)
            except Exception:
                return {}
        return {}

    def _tokenize(self, text: str):
        import re
        if not text:
            return []
        # simple tokenizer splitting on whitespace and punctuation
        tokens = [t for t in re.split(r"[\s,\.\|;:\(\)\"'\u200c]+", text) if t]
        return tokens

    def _normalized_tokens(self, text: str):
        return [t.lower() for t in self._tokenize(text)] if text else []

    def _normalized_text(self, text: str):
        return ' '.join(self._normalized_tokens(text))

    def _find_exact_situation_match(self, sentence: str):
        normalized = self._normalized_text(sentence)
        for idx, item in enumerate(self.proverbs):
            if normalized and self._normalized_text(item.get('situation', '')) == normalized:
                return idx
        return None

    def _lemmatize(self, tokens):
        lemmas = []
        for t in tokens:
            lem = self.lemma_dict.get(t, self.lemma_dict.get(t.lower(), t))
            lemmas.append(lem)
        return lemmas

    def _stem(self, tokens):
        # very small rule-based stemmer: strip common Marathi suffixes
        suffixes = ['णे','ला','ता','ती','ले','चे','ेला','ाला','ने','ता','ाणी','ी','ा','े']
        stems = []
        for t in tokens:
            s = t
            for suf in suffixes:
                if s.endswith(suf) and len(s) - len(suf) >= 2:
                    s = s[: -len(suf)]
                    break
            stems.append(s)
        return stems

    def _pos_tag(self, tokens):
        # heuristic POS tagging: verbs/pronouns/nouns/adjectives
        verb_indicators = set(['कर', 'जा', 'ये', 'वाच', 'शिक', 'दे', 'घ्या', 'लिह'])
        pronouns = set(['मी','तू','तो','ती','ते','आपण','आम्ही','तुम्ही'])
        tags = []
        for t in tokens:
            if t in pronouns or t.lower() in pronouns:
                tags.append('PRON')
            elif t in verb_indicators or t.lower() in verb_indicators:
                tags.append('VERB')
            elif len(t) <= 2:
                tags.append('X')
            else:
                tags.append('NOUN')
        return tags

    def _load_or_build_embeddings(self):
        if PROVERB_EMBEDDINGS_FILE.exists() and SITUATION_EMBEDDINGS_FILE.exists():
            proverb_embeddings = np.load(PROVERB_EMBEDDINGS_FILE)
            situation_embeddings = np.load(SITUATION_EMBEDDINGS_FILE)
            return proverb_embeddings, situation_embeddings

        proverb_texts = [item['proverb'] for item in self.proverbs]
        situation_texts = [item['situation'] or item['proverb'] for item in self.proverbs]
        proverb_embeddings = self.model.encode(proverb_texts, convert_to_numpy=True)
        situation_embeddings = self.model.encode(situation_texts, convert_to_numpy=True)
        EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
        np.save(PROVERB_EMBEDDINGS_FILE, proverb_embeddings)
        np.save(SITUATION_EMBEDDINGS_FILE, situation_embeddings)
        return proverb_embeddings, situation_embeddings

    def recommend(self, sentence, top_k=5):
        exact_idx = self._find_exact_situation_match(sentence)
        query_embedding = self.model.encode([sentence], convert_to_numpy=True)
        scores = cosine_similarity(query_embedding, self.situation_embeddings)[0]
        best_idxs = np.argsort(scores)[::-1].tolist()

        if exact_idx is not None:
            if exact_idx in best_idxs:
                best_idxs.remove(exact_idx)
            best_idxs = [exact_idx] + best_idxs

        best_idxs = best_idxs[:top_k]
        results = []
        for idx in best_idxs:
            item = self.proverbs[idx]
            # preprocessing on the proverb text
            proverb_text = item.get('proverb', '')
            tokens = self._tokenize(proverb_text)
            lemmas = self._lemmatize(tokens)
            stems = self._stem(tokens)
            pos_tags = self._pos_tag(tokens)
            meaning = item.get('meaning', '')
            # produce a simple "meaning_in_depth" by combining stored meaning with context hints
            meaning_in_depth = meaning
            if item.get('situation'):
                meaning_in_depth = meaning_in_depth + ' Context: ' + item.get('situation')
            if item.get('category'):
                meaning_in_depth = meaning_in_depth + ' (Category: ' + item.get('category') + ')'
            results.append({
                'id': item['id'],
                'proverb': item['proverb'],
                'meaning': item['meaning'],
                'meaning_in_depth': meaning_in_depth,
                'situation': item['situation'],
                'category': item['category'],
                'keywords': item['keywords'],
                'emotion': item['emotion'],
                'confidence': float(100.0 if idx == exact_idx else scores[idx] * 100),
                'preprocessing': {
                    'tokens': tokens,
                    'lemmas': lemmas,
                    'stems': stems,
                    'pos_tags': pos_tags,
                },
            })
        return results

engine = RecommendationEngine()
