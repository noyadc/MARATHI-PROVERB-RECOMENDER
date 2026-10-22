from pydantic import BaseModel
from typing import List, Optional, Dict, Any


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
    id: Optional[str] = None
    confidence: Optional[float] = None
    similarity_score: Optional[float] = None
    meaning_in_depth: Optional[str] = None
    source: Optional[str] = "dataset"
    preprocessing: Optional[Dict[str, Any]] = None


class RecommendationRequest(BaseModel):
    sentence: str
    threshold: Optional[float] = None


class RecommendationResponse(BaseModel):
    proverb: str
    meaning: str
    meaning_in_depth: Optional[str] = None
    situation: str
    category: str
    keywords: List[str]
    emotion: str
    confidence: Optional[float] = None
    confidence_label: Optional[str] = None
    source: str = "dataset"
    source_label: str = "Existing Dataset"
    verification_status: str = "verified"
    verification_label: str = "Verified Traditional Proverb"
    verification_details: Optional[str] = None
    source_reference: Optional[str] = None
    source_link: Optional[str] = None
    match_explanation: Optional[str] = None
    fallback_reason: Optional[str] = None
    fallback_notice: Optional[str] = None
    threshold_used: Optional[float] = None
    similarity_score: Optional[float] = None
    top_matches: List[ProverbResponse] = []
    preprocessing: Optional[Dict[str, Any]] = None
