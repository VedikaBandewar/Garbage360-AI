import json
import re


CATEGORY_KEYWORDS = {
    "Organic / Wet Waste": ["food", "vegetable", "fruit", "organic", "wet waste", "kitchen", "rotten", "leaf", "leaves"],
    "Plastic / Dry Waste": ["plastic", "bottle", "bag", "wrapper", "packaging"],
    "Paper Waste": ["paper", "cardboard", "newspaper", "book", "carton"],
    "E-Waste": ["electronic", "e-waste", "battery", "charger", "mobile", "computer", "laptop", "circuit"],
    "Hazardous Waste": ["chemical", "medical", "syringe", "paint", "toxic", "hazardous", "oil"],
}


def keyword_category(text):
    scores = {key: 0 for key in CATEGORY_KEYWORDS}
    for category, words in CATEGORY_KEYWORDS.items():
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", text):
                scores[category] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "Mixed / Unclassified Waste", 0.55
    return best, min(0.95, 0.60 + 0.08 * scores[best])


def has_any(text, words):
    return any(word in text for word in words)


def local_analysis(description, location, existing_reports):
    text = f"{description} {location}".lower()

    category, confidence = keyword_category(text)
    mixed = has_any(text, ["mixed", "garbage pile", "dump", "scattered", "multiple types"])
    drain = has_any(text, ["drain", "gutter", "sewage", "nala", "blocked", "choked", "overflow"])
    large = has_any(text, ["huge", "large", "massive", "big", "road blocked", "roadside pile"])
    public_area = has_any(text, ["school", "college", "hospital", "market", "road", "street", "park"])

    if drain and large:
        severity, drain_risk = "Critical", "High"
    elif drain or large:
        severity, drain_risk = "High", "Medium" if drain else "Low"
    elif mixed or public_area:
        severity, drain_risk = "Medium", "Low"
    else:
        severity, drain_risk = "Low", "Low"

    same_location = sum(
        str(r.get("location", "")).strip().lower() == location.strip().lower()
        for r in existing_reports
    )

    if severity == "Critical":
        priority = "P1"
    elif severity == "High" or same_location >= 3:
        priority = "P2"
    elif severity == "Medium":
        priority = "P3"
    else:
        priority = "P4"

    if drain_risk == "High":
        action = "Immediate drain and garbage clearance; inspect the nearby drainage line."
    elif category == "Mixed / Unclassified Waste":
        action = "Send a waste collection team and perform on-site segregation."
    elif category == "E-Waste":
        action = "Route the material to an authorized e-waste collection point."
    elif category == "Hazardous Waste":
        action = "Escalate to a trained hazardous-waste handling team."
    else:
        action = "Assign the location to the appropriate waste collection team."

    if same_location:
        action += f" Similar location reports found: {same_location}."

    return {
        "category": category,
        "severity": severity,
        "priority": priority,
        "drain_risk": drain_risk,
        "confidence": round(confidence, 2),
        "recommended_action": action,
        "analysis_mode": "Local demo inference",
    }


def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.I)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("AI did not return JSON.")
    return json.loads(match.group(0))


def gemini_analysis(description, location, image_bytes, mime_type, api_key):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are the waste-management AI for Garbage360 AI in India.

Analyze the citizen report below.
Location: {location}
Description: {description}

Return ONLY valid JSON with these keys:
category, severity, priority, drain_risk, confidence, recommended_action

Allowed category values:
Organic / Wet Waste
Plastic / Dry Waste
Paper Waste
E-Waste
Hazardous Waste
Mixed / Unclassified Waste

Allowed severity: Low, Medium, High, Critical
Allowed priority: P1, P2, P3, P4
Allowed drain_risk: Low, Medium, High

Priority meaning:
P1 = immediate/critical
P2 = high
P3 = medium
P4 = low

confidence must be a number from 0 to 1.
Do not invent a precise GPS coordinate.
Keep recommended_action practical and short.
"""

    contents = [prompt]
    if image_bytes:
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type or "image/jpeg",
            )
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
    )

    result = _extract_json(response.text)
    result["confidence"] = float(result.get("confidence", 0.75))
    result["analysis_mode"] = "Gemini multimodal AI"
    return result


def analyze_report(
    description,
    location,
    existing_reports,
    image_bytes=None,
    mime_type=None,
    api_key=None,
):
    # Use real multimodal AI when a key is configured.
    if api_key:
        try:
            result = gemini_analysis(
                description, location, image_bytes, mime_type, api_key
            )
            return result
        except Exception:
            # Never make the app unusable because the optional AI service failed.
            pass

    return local_analysis(description, location, existing_reports)
