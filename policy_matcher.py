import os
import json
from typing import Dict, Any

def get_fallback_schemes(crop_type: str, land_size: str, income_range: str, state: str) -> Dict[str, Any]:
    """Rule-based engine providing high-quality matching schemes when LLM key is absent or failing."""
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

    # Add state-specific customization if available
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
    elif "andhra" in state_lower:
        schemes.append({
            "name": "YSR Rythu Bharosa",
            "description": "State financial assistance program for farmer families including tenant farmers.",
            "benefit": "₹13,500 per year.",
            "how_to_apply": "Apply through Rythu Bharosa Kendras (RBKs)."
        })

    return {"schemes": schemes}


def get_policy_matches(crop_type: str, land_size: str, income_range: str, state: str) -> Dict[str, Any]:
    """Matches eligible schemes using Google Gemini LLM API if key is set, else uses rules engine fallback."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key and api_key.strip():
        try:
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

            Identify all top 3 to 5 relevant government agricultural schemes, subsidies, crop insurance, or credit programs this farmer is eligible for in India and specifically in {state}.

            Return JSON matching this exact schema:
            {{
              "schemes": [
                {{
                  "name": "Exact Name of Scheme",
                  "description": "Clear 2-sentence summary of the scheme purpose",
                  "benefit": "Specific financial support or subsidy details (e.g., ₹6000/year or 50% equipment subsidy)",
                  "how_to_apply": "Actionable application steps or official portal link"
                }}
              ]
            }}
            Do not include Markdown code fences or extra text, return ONLY valid JSON.
            """

            # Try Flash models available on Gemini API
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
                        break
                except Exception as m_err:
                    print(f"[PolicyMatcher] Model {m_name} failed: {m_err}, trying next...")
                    continue

            if response and response.text:
                result = json.loads(response.text)
                if "schemes" in result and isinstance(result["schemes"], list) and len(result["schemes"]) > 0:
                    return result
        except Exception as e:
            print(f"[PolicyMatcher] Gemini API execution failed/fallback: {e}")

    # Fallback to rich rules engine
    return get_fallback_schemes(crop_type, land_size, income_range, state)
