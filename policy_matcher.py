import os
import json
import logging
from typing import Dict, Any
from config import settings

logger = logging.getLogger("farmconnect.policy_matcher")

# Thread-safe in-memory cache to reduce latency & API costs
POLICY_CACHE: Dict[str, Dict[str, Any]] = {}

def get_fallback_schemes(crop_type: str, land_size: str, income_range: str, state: str) -> Dict[str, Any]:
    """Rule-based engine providing high-quality matching schemes independently testable."""
    schemes = [
        {
            "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
            "description": "Central sector scheme providing income support to small and marginal farmer families across India.",
            "benefit": "₹6,000 per year paid in 3 equal installments directly into bank account.",
            "how_to_apply": "Apply via pmkisan.gov.in portal or visit nearest Common Service Centre (CSC) with Aadhaar and land records."
        },
        {
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "description": f"Comprehensive crop insurance scheme protecting {crop_type} crops against non-preventable natural risks, pests & diseases.",
            "benefit": "Full financial cover for crop damage with low premium (1.5% to 2% for food crops).",
            "how_to_apply": "Enroll through your crop loan bank branch or register online at pmfby.gov.in within notified cut-off date."
        },
        {
            "name": "Kisan Credit Card (KCC) Scheme",
            "description": "Provides timely access to short-term credit for crop cultivation, harvest expenses, and equipment maintenance.",
            "benefit": "Concessional interest rate at 4% per annum for prompt repayment on loans up to ₹3 Lakh.",
            "how_to_apply": "Submit KCC application form at any Commercial Bank, RRB, or Cooperative Bank."
        },
        {
            "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
            "description": "Subsidy program to promote farm mechanization and equipment ownership among smallholders.",
            "benefit": "40% to 50% financial subsidy on tractors, tillers, harvesters, and sprayers.",
            "how_to_apply": "Register on agrimachinery.nic.in and submit land record proof."
        }
    ]

    state_lower = state.lower()
    if "kerala" in state_lower or "palakkad" in state_lower or "thrissur" in state_lower:
        schemes.append({
            "name": "Subhiksha Keralam Scheme",
            "description": "State government incentive program for fallow land cultivation and vegetable farming.",
            "benefit": "Financial grant up to ₹40,000 per hectare for food crops.",
            "how_to_apply": "Contact Krishi Bhavan officer in your local Grama Panchayat."
        })
    elif "telangana" in state_lower:
        schemes.append({
            "name": "Rythu Bandhu Scheme",
            "description": "Financial assistance for purchasing inputs like seeds, fertilizers, and pesticides.",
            "benefit": "₹10,000 per acre per year.",
            "how_to_apply": "Register details with Agriculture Extension Officer (AEO)."
        })

    return {"schemes": schemes}


def query_gemini_llm(crop_type: str, land_size: str, income_range: str, state: str) -> Dict[str, Any]:
    """Independent function calling Google Gemini API with model fallback."""
    api_key = settings.GEMINI_API_KEY
    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key is not configured.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = f"""
    You are an expert Indian Government Agriculture Policy Advisor.
    A farmer submitted their details:
    - Crop Type: {crop_type}
    - Land Size: {land_size}
    - Income Range: {income_range}
    - State/Location: {state}

    Identify top 3 to 5 relevant government agricultural schemes, subsidies, crop insurance, or credit programs this farmer is eligible for in India and specifically in {state}.

    Return JSON matching this exact schema:
    {{
      "schemes": [
        {{
          "name": "Exact Name of Scheme",
          "description": "Clear 2-sentence summary of the scheme purpose",
          "benefit": "Specific financial support or subsidy details",
          "how_to_apply": "Actionable application steps or official portal link"
        }}
      ]
    }}
    Return ONLY valid JSON.
    """

    model_names = ['gemini-3.5-flash', 'gemini-3.6-flash', 'gemini-3.8-flash', 'gemini-2.5-flash']
    response = None

    for m_name in model_names:
        try:
            response = client.models.generate_content(
                model=m_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            if response and response.text:
                logger.info(f"Successfully generated policies using model {m_name}")
                break
        except Exception as m_err:
            logger.warning(f"Gemini model {m_name} failed: {m_err}")
            continue

    if response and response.text:
        result = json.loads(response.text)
        if "schemes" in result and isinstance(result["schemes"], list) and len(result["schemes"]) > 0:
            return result

    raise RuntimeError("No valid response from Gemini API models.")


def get_policy_matches(crop_type: str, land_size: str, income_range: str, state: str) -> Dict[str, Any]:
    """Matches policy schemes using in-memory cache, Gemini LLM API, or rule-based engine fallback."""
    cache_key = f"{crop_type.strip().lower()}|{land_size.strip().lower()}|{income_range.strip().lower()}|{state.strip().lower()}"
    
    # 1. Check in-memory cache
    if cache_key in POLICY_CACHE:
        logger.info(f"Serving policy matches from in-memory cache for key: {cache_key}")
        return POLICY_CACHE[cache_key]

    # 2. Query Gemini LLM
    try:
        res = query_gemini_llm(crop_type, land_size, income_range, state)
        POLICY_CACHE[cache_key] = res
        return res
    except Exception as e:
        logger.error(f"Gemini LLM policy query failed: {e}. Falling back to rule-based engine.")

    # 3. Fallback to rule engine
    fallback = get_fallback_schemes(crop_type, land_size, income_range, state)
    POLICY_CACHE[cache_key] = fallback
    return fallback
