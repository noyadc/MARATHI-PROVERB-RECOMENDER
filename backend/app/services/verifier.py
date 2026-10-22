import csv
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

BASE_DIR = Path(__file__).resolve().parents[3]
VERIFIED_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "verified_marathi_proverbs.json"
DATASET_PATH = BASE_DIR / "dataset" / "marathi_proverbs_200.csv"


def normalize_proverb_text(text: str) -> str:
    """Normalize Marathi proverb string for consistent matching."""
    if not text:
        return ""
    # Remove punctuation, punctuation marks, quotation marks, and standardize spaces
    cleaned = re.sub(r"[\.,;:!\?\"'\|॥\(\)\[\]\{\}\s\u200c\u200d]+", " ", text).strip().lower()
    return cleaned


class ProverbVerifier:
    def __init__(self):
        self.verified_records: Dict[str, Dict[str, Any]] = {}
        self._load_curated_verified_proverbs()
        self._load_dataset_proverbs()

    def _load_curated_verified_proverbs(self):
        if VERIFIED_DATA_PATH.exists():
            try:
                with open(VERIFIED_DATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("proverbs", []):
                        norm = normalize_proverb_text(item.get("proverb", ""))
                        if norm:
                            self.verified_records[norm] = {
                                "proverb": item.get("proverb", ""),
                                "meaning": item.get("meaning", ""),
                                "category": item.get("category", ""),
                                "source": item.get("source", "पारंपरिक मराठी म्हणी संग्रह"),
                                "reference_link": item.get("reference_link", data.get("canonical_reference", "")),
                                "origin": "curated_reference",
                            }
            except Exception as e:
                # Keep service operational even if external file has an issue
                pass

    def _load_dataset_proverbs(self):
        if DATASET_PATH.exists():
            try:
                with open(DATASET_PATH, "r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        raw_prov = row.get("Proverb") or row.get("proverb") or ""
                        norm = normalize_proverb_text(raw_prov)
                        if norm and norm not in self.verified_records:
                            self.verified_records[norm] = {
                                "proverb": raw_prov.strip(),
                                "meaning": (row.get("Meaning") or row.get("meaning") or "").strip(),
                                "category": (row.get("Category") or row.get("category") or "").strip(),
                                "source": "मराठी म्हणी प्रमाणित डेटासेट (Curated Dataset)",
                                "reference_link": "https://mr.wikipedia.org/wiki/मराठी_म्हणी",
                                "origin": "dataset",
                            }
            except Exception:
                pass

    def verify(self, proverb_text: str, ai_source: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify whether the provided proverb text matches an established,
        authentic Marathi proverb in our curated or dataset records.
        """
        if not proverb_text or not proverb_text.strip():
            return {
                "is_verified": False,
                "verification_status": "not_found",
                "verification_label": "No Authentic Proverb Found",
                "verification_details": "कोणतीही अस्सल म्हण उपलब्ध नाही.",
                "source_reference": None,
                "source_link": None,
            }

        normalized = normalize_proverb_text(proverb_text)

        # Check for direct match
        matched_record = self.verified_records.get(normalized)

        # Also check if partial or sub-phrase matches if exact normalized key wasn't found
        if not matched_record:
            for key, record in self.verified_records.items():
                if len(key) >= 6 and (key in normalized or normalized in key):
                    # Check token overlap ratio
                    k_tokens = set(key.split())
                    n_tokens = set(normalized.split())
                    if len(k_tokens) > 0 and len(n_tokens) > 0:
                        overlap = len(k_tokens & n_tokens) / max(len(k_tokens), len(n_tokens))
                        if overlap >= 0.8:
                            matched_record = record
                            break

        if matched_record:
            return {
                "is_verified": True,
                "verification_status": "verified",
                "verification_label": "Verified Traditional Proverb",
                "verification_details": f"पडताळणी यशस्वी: ही म्हण प्रमाणित मराठी संदर्भामध्ये उपलब्ध आहे ({matched_record['source']}).",
                "source_reference": matched_record["source"],
                "source_link": matched_record.get("reference_link"),
            }
        else:
            # Unverified external/AI suggestion
            source_ref = ai_source.strip() if ai_source and ai_source.strip() else "अपुष्टीकृत संदर्भ (Unverified Source)"
            return {
                "is_verified": False,
                "verification_status": "unverified",
                "verification_label": "Unverified AI Suggestion",
                "verification_details": "अपुष्टीकृत: ही म्हण आमच्या प्रमाणित पारंपरिक संकलनात थेट आढळली नाही. कृपया याची सत्यता तपासावी.",
                "source_reference": source_ref,
                "source_link": None,
            }

    def is_duplicate(self, proverb_a: str, proverb_b: str) -> bool:
        """Check if two proverb texts represent the same proverb."""
        norm_a = normalize_proverb_text(proverb_a)
        norm_b = normalize_proverb_text(proverb_b)
        if not norm_a or not norm_b:
            return False
        if norm_a == norm_b:
            return True
        tok_a = set(norm_a.split())
        tok_b = set(norm_b.split())
        if tok_a and tok_b:
            overlap = len(tok_a & tok_b) / max(len(tok_a), len(tok_b))
            return overlap >= 0.85
        return False


verifier = ProverbVerifier()
