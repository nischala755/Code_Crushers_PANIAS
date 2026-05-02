"""
Mistral AI integration for query interpretation and explanation generation.
"""

import json
import re
import os
from mistralai import Mistral

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

client = None


def get_client():
    global client
    if client is None:
        client = Mistral(api_key=MISTRAL_API_KEY)
    return client


def interpret_query(natural_query: str) -> dict:
    """
    Use Mistral to interpret a natural language query into structured filters.
    Returns a dict with filter fields.
    """
    try:
        c = get_client()
        prompt = f"""You are a government database query interpreter for Karnataka state business registry.

Convert the following natural language query into a structured JSON filter.

Available filter fields:
- activity_status: "ACTIVE", "DORMANT", "CLOSED"
- department: "SHOPS_ESTABLISHMENT", "FACTORIES", "LABOUR", "POLLUTION_BOARD"
- city: city name (e.g., "Bengaluru", "Mysuru")
- pincode: 6-digit pincode
- risk_level: "LOW", "MEDIUM", "HIGH"
- no_inspection_months: number of months without inspection (integer)
- business_type: keywords from business name
- min_confidence: minimum confidence score (0-1)

Return ONLY valid JSON. No explanation. Example:
{{"activity_status": "ACTIVE", "pincode": "560058", "no_inspection_months": 18, "department": "FACTORIES"}}

Query: "{natural_query}"

JSON:"""

        response = c.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300,
        )

        text = response.choices[0].message.content.strip()
        # Extract JSON from response
        json_match = re.search(r'\{[^}]+\}', text)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(text)

    except Exception as e:
        print(f"[MISTRAL] Query interpretation failed: {e}")
        return fallback_interpret(natural_query)


def fallback_interpret(query: str) -> dict:
    """Keyword-based fallback when Mistral is unavailable."""
    q = query.lower()
    filters = {}

    # Activity status
    if "active" in q:
        filters["activity_status"] = "ACTIVE"
    elif "dormant" in q:
        filters["activity_status"] = "DORMANT"
    elif "closed" in q:
        filters["activity_status"] = "CLOSED"

    # Department
    if "factor" in q:
        filters["department"] = "FACTORIES"
    elif "shop" in q or "establishment" in q:
        filters["department"] = "SHOPS_ESTABLISHMENT"
    elif "labour" in q or "labor" in q:
        filters["department"] = "LABOUR"
    elif "pollution" in q:
        filters["department"] = "POLLUTION_BOARD"

    # Pincode
    pincode_match = re.search(r'\b(\d{6})\b', q)
    if pincode_match:
        filters["pincode"] = pincode_match.group(1)

    # City
    cities = ["bengaluru", "bangalore", "mysuru", "mysore", "hubli", "dharwad", "mangaluru", "mangalore"]
    for city in cities:
        if city in q:
            filters["city"] = city.capitalize()
            if city == "bangalore":
                filters["city"] = "Bengaluru"
            if city == "mysore":
                filters["city"] = "Mysuru"
            if city == "mangalore":
                filters["city"] = "Mangaluru"
            break

    # No inspection
    insp_match = re.search(r'no\s+inspection\s+(?:in\s+)?(\d+)\s+months?', q)
    if insp_match:
        filters["no_inspection_months"] = int(insp_match.group(1))

    # Risk
    if "high risk" in q:
        filters["risk_level"] = "HIGH"
    elif "medium risk" in q:
        filters["risk_level"] = "MEDIUM"
    elif "low risk" in q:
        filters["risk_level"] = "LOW"

    return filters


def generate_explanation(context: dict) -> str:
    """Generate a human-readable explanation for a match or classification."""
    try:
        c = get_client()
        prompt = f"""You are a government data analyst. Generate a brief, professional explanation (2-3 sentences) for the following data context.
Be factual and specific. Use formal government report language.

Context: {json.dumps(context)}

Explanation:"""

        response = c.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[MISTRAL] Explanation generation failed: {e}")
        return ""
