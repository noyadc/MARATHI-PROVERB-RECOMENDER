from pydantic import BaseModel
from typing import List, Optional

class ProverbBase(BaseModel):
    proverb: str
    meaning: str
    situation: str
    category: str
    keywords: List[str]
    emotion: str

class ProverbCreate(ProverbBase):
    pass

class ProverbResponse(ProverbBase):
    id: str
    confidence: Optional[float] = None
    meaning_in_depth: Optional[str] = None
    preprocessing: Optional[dict] = None

class RecommendationRequest(BaseModel):
    sentence: str

class RecommendationResponse(BaseModel):
    proverb: str
    meaning: str
    meaning_in_depth: Optional[str] = None
    situation: str
    category: str
    keywords: List[str]
    emotion: str
    confidence: float
    top_matches: List[ProverbResponse]
