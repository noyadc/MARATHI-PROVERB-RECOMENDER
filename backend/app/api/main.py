from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import auth, proverbs, recommendation, analytics

app = FastAPI(
    title="Marathi Proverb Recommendation System",
    description="API backend for Marathi proverb recommendation with semantic retrieval.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(proverbs.router, prefix="/api/proverbs", tags=["Proverbs"])
app.include_router(recommendation.router, prefix="/api/recommend", tags=["Recommendation"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
