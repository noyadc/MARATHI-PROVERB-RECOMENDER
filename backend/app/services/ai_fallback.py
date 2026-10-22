import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded
BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / ".env"
BACKEND_ENV_PATH = BASE_DIR / "backend" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
elif BACKEND_ENV_PATH.exists():
    load_dotenv(BACKEND_ENV_PATH)
else:
    load_dotenv()

from .verifier import verifier

logger = logging.getLogger("ai_fallback")

SYSTEM_PROMPT = """You are a distinguished scholar of Marathi language, classical literature, and folklore (मराठी म्हणी व लोकसंस्कृती तज्ज्ञ).
Your task is to identify an authentic, traditional Marathi proverb (अस्सल व पारंपरिक मराठी म्हण) that best fits the given real-life situation.

CRITICAL RULES:
1. Real traditional proverbs only: Prefer a genuine, established Marathi proverb that is recognized in Marathi culture and lexicography. DO NOT invent, translate, or fabricate a new saying.
2. Honesty and hallucination prevention: If you cannot find or identify a genuine, authentic traditional Marathi proverb that truly matches this situation, you MUST set "authentic_proverb_found": false and leave "proverb" empty. Do NOT force a modern translation or invent a proverb.
3. Accurate cultural explanation: Provide the authentic meaning and explain why this proverb traditionally fits.
4. Cite sources: If you know the traditional origin or literary/dictionary reference, provide it under "traditional_source".

Respond ONLY with a valid JSON object matching this exact structure:
{
  "authentic_proverb_found": true,
  "proverb": "अस्सल पारंपारिक मराठी म्हण",
  "meaning": "म्हणीचा मुख्य अर्थ (मराठीत)",
  "meaning_in_depth": "म्हणीचा सविस्तर अर्थ आणि सांस्कृतिक संदर्भ (मराठीत)",
  "situation": "ज्या परिस्थितीत ही म्हण वापरली जाते त्याचे वर्णन",
  "category": "श्रेणी (उदा. शहाणपण, अनुभव, नीती, व्यवहार, शिक्षण)",
  "emotion": "भावना (उदा. सावधगिरी, उपहास, बोध, प्रेरणा)",
  "keywords": ["कीवर्ड1", "कीवर्ड2", "keyword1"],
  "match_explanation": "ही म्हण या परिस्थितीशी का आणि कशी सुसंगत आहे याचे थोडक्यात स्पष्टीकरण",
  "traditional_source": "पारंपरिक संदर्भ किंवा स्रोत (उदा. मोल्सवर्थ शब्दकोश, महाराष्ट्र साहित्य परिषद, लोकपरंपरा)"
}"""


async def get_ai_fallback_recommendation(sentence: str) -> Dict[str, Any]:
    """
    Calls the OpenAI API as a fallback when the local dataset does not
    contain a sufficiently relevant match.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        logger.info("OPENAI_API_KEY is not set. Gracefully bypassing AI fallback.")
        return {
            "status": "failed_missing_api_key",
            "error_detail": "OPENAI_API_KEY is not configured.",
            "notice": "OpenAI API Key (OPENAI_API_KEY) सेट केलेले नाही. स्थानिक डेटासेटमधील सर्वात जवळचे पर्याय दर्शविले आहेत.",
            "data": None,
        }

    try:
        from openai import OpenAI, APIError, RateLimitError, APITimeoutError, AuthenticationError
    except ImportError:
        logger.error("openai package is not installed.")
        return {
            "status": "failed_dependency",
            "error_detail": "openai package is not installed in python environment.",
            "notice": "OpenAI पॅकेज उपलब्ध नाही. स्थानिक डेटासेट परिणाम दर्शविले आहेत.",
            "data": None,
        }

    try:
        client = OpenAI(api_key=api_key, timeout=18.0)

        user_content = f"खालील परिस्थितीसाठी अस्सल पारंपारिक मराठी म्हण शोधा:\n\n{sentence}"

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=650,
        )

        raw_content = completion.choices[0].message.content
        if not raw_content:
            return {
                "status": "failed_empty_response",
                "error_detail": "Empty completion received from OpenAI.",
                "notice": "AI मॉडेलकडून रिकामा प्रतिसाद मिळाला.",
                "data": None,
            }

        parsed = json.loads(raw_content)
        found = bool(parsed.get("authentic_proverb_found", False))
        proverb_text = (parsed.get("proverb") or "").strip()

        if not found or not proverb_text:
            return {
                "status": "authentic_proverb_not_found",
                "error_detail": "AI model confirmed that no authentic traditional proverb matches this situation.",
                "notice": "या प्रसंगासाठी कोणतीही अस्सल पारंपारिक म्हण उपलब्ध नाही. बनावट म्हण तयार न करता स्थानिक डेटासेटमधील सर्वात जवळचे पर्याय दर्शविले आहेत.",
                "data": None,
            }

        # Verify the AI suggestion against authentic curated collections
        traditional_source = parsed.get("traditional_source")
        verification = verifier.verify(proverb_text, ai_source=traditional_source)

        return {
            "status": "success",
            "notice": None,
            "data": {
                "proverb": proverb_text,
                "meaning": (parsed.get("meaning") or "").strip(),
                "meaning_in_depth": (parsed.get("meaning_in_depth") or parsed.get("meaning") or "").strip(),
                "situation": (parsed.get("situation") or sentence).strip(),
                "category": (parsed.get("category") or "सामान्य").strip(),
                "emotion": (parsed.get("emotion") or "बोध").strip(),
                "keywords": [str(kw).strip() for kw in parsed.get("keywords", []) if str(kw).strip()],
                "match_explanation": (parsed.get("match_explanation") or "").strip(),
                "verification_status": verification["verification_status"],
                "verification_label": verification["verification_label"],
                "verification_details": verification["verification_details"],
                "source_reference": verification["source_reference"] or traditional_source,
                "source_link": verification.get("source_link"),
            },
        }

    except AuthenticationError:
        logger.warning("OpenAI API authentication failed (invalid API key).")
        return {
            "status": "failed_auth",
            "error_detail": "Invalid OpenAI API Key.",
            "notice": "OpenAI API Key अमान्य (Invalid) आहे. कृपया वैध API की प्रविष्ट करा.",
            "data": None,
        }
    except RateLimitError:
        logger.warning("OpenAI API rate limit or quota exceeded.")
        return {
            "status": "failed_rate_limit",
            "error_detail": "OpenAI rate limit or quota exceeded.",
            "notice": "OpenAI API मर्यादा (Rate Limit / Quota) संपली आहे. स्थानिक पर्याय दर्शविले आहेत.",
            "data": None,
        }
    except APITimeoutError:
        logger.warning("OpenAI API request timed out.")
        return {
            "status": "failed_timeout",
            "error_detail": "OpenAI request timed out after 18 seconds.",
            "notice": "OpenAI सर्व्हर प्रतिसाद वेळेत मिळाला नाही. स्थानिक पर्याय दर्शविले आहेत.",
            "data": None,
        }
    except APIError as e:
        logger.error(f"OpenAI API error occurred: {type(e).__name__}")
        return {
            "status": "failed_api_error",
            "error_detail": f"OpenAI API Error: {type(e).__name__}",
            "notice": "OpenAI सर्व्हरमध्ये तांत्रिक अडचण आली. स्थानिक पर्याय दर्शविले आहेत.",
            "data": None,
        }
    except Exception as e:
        logger.error(f"Unexpected error in AI fallback: {type(e).__name__}")
        return {
            "status": "failed_unexpected",
            "error_detail": f"Unexpected error: {type(e).__name__}",
            "notice": "AI फॉलबॅक दरम्यान अनपेक्षित त्रुटी आली. स्थानिक पर्याय दर्शविले आहेत.",
            "data": None,
        }
