# Marathi Proverb Recommendation System

A React app and FastAPI backend that recommend a Marathi proverb from a situation or sentence. The backend uses sentence embeddings and the proverb dataset in `dataset/marathi_proverbs_200.csv`.

## Requirements

- Windows 10 or later
- Python 3.10 or 3.11
- Node.js 18 or later with npm
- Internet access the first time the recommendation model is loaded

MongoDB is not required for the recommendation, proverb, or analytics endpoints in this project.

## Setup

Run these commands from the project root in PowerShell. Use the project virtual environment for every backend command; a different globally installed Python may have incompatible package versions.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Install the frontend dependencies:

```powershell
cd frontend
npm ci
cd ..
```

## Run the application

Open two PowerShell terminals from the project root.

In the first terminal, start the backend:

```powershell
cd backend
..\.venv\Scripts\python.exe backend_start.py
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`. The first startup may download the `sentence-transformers/LaBSE` model; allow it to finish before sending recommendations.

In the second terminal, start the frontend:

```powershell
cd frontend
npm start
```

The frontend opens at `http://localhost:3000`. Keep both terminals running while using the app. Stop either server with `Ctrl+C`.

## Environment Configuration (AI Fallback)

Copy `.env.example` to `.env` in the project root:

```powershell
Copy-Item .env.example .env
```

Set your configuration values inside `.env`:
- `OPENAI_API_KEY`: Your OpenAI API Key (e.g. `sk-...`). If not set, the system gracefully continues using closest dataset matches with an informative notice.
- `OPENAI_MODEL`: Model name (default `gpt-4o-mini`).
- `SIMILARITY_THRESHOLD`: Minimum similarity threshold (default `0.45`). When the best match from the local dataset is below this score and not an exact match, the AI fallback is activated.

## Main API endpoints

- `POST /api/recommend` accepts JSON such as:
  ```json
  {
    "sentence": "अभ्यास न करता परीक्षेला जाणे",
    "threshold": 0.45
  }
  ```
  Returns recommendation with source (`dataset` or `ai_fallback`), verification status (`verified`, `unverified`, `not_found`), source reference, match explanation, confidence/similarity score, top matches, and NLP preprocessing details.
- `GET /api/proverbs` lists the proverb dataset.
- `GET /api/proverbs/{id}` gets one proverb by ID.
- `GET /api/analytics/summary` returns category and emotion counts.
- `POST /api/auth/login` accepts form data for the demo login.

The current demo login is `admin` / `admin123`. It is hard-coded for development and must be replaced before deploying this project publicly.

## Run backend tests

Install the test-only packages if needed, then run the tests from `backend`:

```powershell
..\.venv\Scripts\python.exe -m pip install pytest httpx
..\.venv\Scripts\python.exe -m pytest -v test_recommend.py
```

## Dual Pipeline Architecture (Dataset + AI Fallback)

1. **Step 1: Search Existing Dataset**
   - User's Marathi situation is normalized and embedded using `sentence-transformers/LaBSE`.
   - Cosine similarity is computed against precomputed situation, composite, and meaning embeddings.
   - Exact-match override is applied.
2. **Step 2: Relevance & Configurable Threshold**
   - If an exact match exists or the best similarity meets `SIMILARITY_THRESHOLD`, the dataset proverb is returned.
   - If similarity is below threshold, AI fallback activates.
3. **Step 3: OpenAI Generative Fallback**
   - Calls OpenAI with strict instructions to identify real, traditional Marathi proverbs (मराठी म्हणी) without fabricating or hallucinating sayings.
   - If no authentic proverb matches, the model declares `authentic_proverb_found: false`.
4. **Step 4: Verification Service**
   - Proverb is verified against curated traditional reference collections (`verified_marathi_proverbs.json` and `marathi_proverbs_200.csv`).
   - Sourced proverbs are labeled `Verified Traditional Proverb`; unsourced sayings are flagged `Unverified AI Suggestion`.
   - Duplicates are prevented in results.
5. **Step 5: Frontend Presentation**
   - Source pill (`Existing Dataset` vs `AI Fallback`), verification badges, confidence/similarity score, explanation of fit, source citations, preprocessing breakdown, and closest dataset matches.

## Troubleshooting

- **FastAPI/Starlette startup error:** use `.venv\Scripts\python.exe` as shown above. Do not start the backend with a different global `python` installation.
- **Frontend cannot reach the API:** make sure the backend is running on port 8000. The frontend currently calls `http://localhost:8000/api/recommend` directly.
- **Model download or network error:** the backend loads `sentence-transformers/LaBSE` on startup. Check internet access and retry after the model download completes.
- **OpenAI Fallback Notice:** If `OPENAI_API_KEY` is omitted, the app displays closest dataset matches with a clear notice.
- **Port already in use:** stop the process using port 8000 or 3000, then restart the corresponding app.

## Project layout

- `backend/` - FastAPI app, recommendation engine, fallback services, and backend tests
  - `backend/app/recommendation/engine.py` - LaBSE embedding search & NLP preprocessing
  - `backend/app/services/ai_fallback.py` - OpenAI fallback integration
  - `backend/app/services/verifier.py` - Proverb verification & deduplication service
  - `backend/app/data/verified_marathi_proverbs.json` - Curated collection of authentic traditional Marathi proverbs
- `dataset/marathi_proverbs_200.csv` - proverb data
- `backend/embeddings/` - precomputed proverb and situation embeddings
- `frontend/` - React application with dynamic source & verification indicators
- `preprocessing/lemma_dictionary.json` - Marathi lemma mappings
- `.env.example` - Example configuration file