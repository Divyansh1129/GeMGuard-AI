"""
llm_service.py
----------------
Uses Groq's API (free tier) to run an open-source LLM (Llama 3.3 70B).
Groq's API is OpenAI-compatible in shape.

TWO jobs, both prompting only — no fine-tuning needed for either.

JOB 1 — extract_fields():
  Input: raw OCR text of a document
  Output: structured JSON (GSTIN, PAN, dates, names, numbers) pulled out of messy text

JOB 2 — generate_recommendation():
  Input: rule-engine results + ML risk score for a bidder
  Output: natural-language recommendation for the Procurement Officer

API used: Groq Chat Completions API
Docs: https://console.groq.com/docs/quickstart
Auth: GROQ_API_KEY (set in .env, get one free from console.groq.com)
"""

import json
import re
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None


def _decode_json_object(value: str) -> dict:
    """Accept a JSON object even when a provider adds prose or code fences."""
    start = value.find("{")
    if start < 0:
        raise ValueError("No JSON object in extraction response")
    depth, quoted, escaped = 0, False, False
    for index, char in enumerate(value[start:], start):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                parsed = json.loads(value[start:index + 1])
                if not isinstance(parsed, dict):
                    raise ValueError("Extraction response was not an object")
                return parsed
    raise ValueError("Unterminated JSON object in extraction response")


def _fallback_fields(doc_type: str, raw_text: str) -> dict:
    """Extract only evidence present in the uploaded text; never invent a result."""
    text = " ".join(raw_text.split())
    fields = {"document_type": doc_type, "extraction_method": "regex_fallback"}
    patterns = {
        "pan": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        "gstin": r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z][Z][0-9A-Z]\b",
        "udyam_number": r"\bUDYAM-[A-Z]{2}-\d{2}-\d{7}\b",
        "epfo_number": r"\b[A-Z]{2}[A-Z0-9]{5,18}\b",
        "esic_number": r"\b\d{10,17}\b",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[key] = match.group(0).upper()
    date_match = re.search(r"\b(?:\d{1,2}[/-]){2}\d{2,4}\b", text)
    if date_match:
        fields["issue_date"] = date_match.group(0)
    label_match = re.search(r"(?:Name of (?:the )?(?:Enterprise|Assessee|Employer)|Legal Name|Name)\s*[:\-]\s*([^\n]{3,100})", raw_text, re.IGNORECASE)
    if label_match:
        fields["legal_name"] = label_match.group(1).strip()
    fields["confidence"] = 0.55 if any(k in fields for k in ("pan", "gstin", "udyam_number")) else 0.2
    return fields


def extract_fields(doc_type: str, raw_text: str) -> dict:
    """Ask the LLM to pull structured fields out of messy OCR text."""
    if not raw_text.strip():
        return {"document_type": doc_type, "confidence": 0, "error": "No text could be extracted from the uploaded file."}
    if not client:
        return _fallback_fields(doc_type, raw_text)
    prompt = f"""You are an evidence-only extraction service for Indian procurement documents.
Document type: {doc_type}
Raw OCR text:
---
{raw_text[:4000]}
---
Return ONLY a JSON object with these optional keys: legal_name, document_id, pan,
gstin, udyam_number, epfo_number, esic_number, issue_date, valid_until, authority,
confidence. Copy values exactly from the text. Do not infer, complete, or invent values.
confidence must be 0 to 1 and reflect text quality. Omit unavailable fields."""

    try:
        response = client.chat.completions.create(model=settings.LLM_MODEL, max_tokens=500, messages=[{"role": "user", "content": prompt}])
        raw = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        extracted = _decode_json_object(raw)
        extracted["document_type"] = doc_type
        extracted["extraction_method"] = "llm"
        extracted["confidence"] = max(0, min(1, float(extracted.get("confidence", 0))))
        return extracted
    except Exception as exc:
        fallback = _fallback_fields(doc_type, raw_text)
        # Provider output must never become a false evidence field or leak into the review UI.
        fallback["extraction_status"] = "llm_unavailable_or_malformed_response; deterministic extraction used"
        return fallback


def extract_tender_requirements(raw_text: str) -> list[dict]:
    """Derive only requirements explicitly evidenced in an uploaded tender."""
    text = " ".join(raw_text.split())
    requirements = []
    patterns = [("gst", "GST Registration", r"\bGST(?:IN)?\b"), ("pan", "PAN", r"\bPAN\b"), ("udyam", "Udyam/MSME Registration", r"\b(?:UDYAM|MSME)\b"), ("epfo", "EPFO Compliance", r"\bEPFO\b"), ("esic", "ESIC Compliance", r"\bESIC\b"), ("oem_auth", "OEM Authorization", r"\bOEM\b"), ("non_blacklisting", "Non-Blacklisting Declaration", r"\b(?:blacklist|debar)"), ("startup_india", "Startup India Certificate", r"\bStartup India\b")]
    for key, label, pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            requirements.append({"requirement_key": key, "label": label, "mandatory": True, "verification_type": "document_evidence", "source_evidence": label})
    match = re.search(r"(?:local content|Make in India).{0,80}?(\d{1,3})\s*%", text, re.IGNORECASE)
    if match:
        requirements.append({"requirement_key": "local_content", "label": "Local Content", "mandatory": True, "minimum_value": float(match.group(1)), "unit": "percentage", "verification_type": "document_evidence", "source_evidence": match.group(0)})
    expected_patterns = [
        ("expected_legal_name", "Required legal entity", r"(?:required\s+)?(?:bidder\s+)?legal\s+entity\s*[:\-]\s*([^\n\r]+)"),
        ("expected_pan", "Required PAN", r"(?:required\s+)?PAN(?:\s+(?:number|ID))?\s*[:\-]\s*([A-Z]{5}\d{4}[A-Z])"),
        ("expected_gstin", "Required GSTIN", r"(?:required\s+)?GSTIN\s*[:\-]\s*([0-9]{2}[A-Z]{5}\d{4}[A-Z][0-9A-Z]Z[0-9A-Z])"),
        ("expected_udyam_number", "Required Udyam registration", r"(?:required\s+)?Udyam(?:\s+(?:registration\s+)?(?:number|no\.?))?\s*[:\-]\s*(UDYAM-[A-Z]{2}-\d{2}-\d{7})"),
    ]
    for key, label, pattern in expected_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            requirements.append({
                "requirement_key": key,
                "label": label,
                "mandatory": True,
                "verification_type": "value_match",
                "source_evidence": " ".join(match.group(1).strip().rstrip(".").split()).upper(),
            })
    return requirements

def generate_recommendation(bidder_name: str, rule_results: dict, ml_risk_prob: float,
                             compliance_score: float, risk_level: str) -> str:
    """Ask the LLM to turn structured check results into a readable recommendation."""
    prompt = f"""You are assisting a Government e-Marketplace (GeM) Procurement Officer.
Bidder: {bidder_name}
Compliance Score: {compliance_score}/100
Risk Level: {risk_level}
ML model's predicted high-risk probability: {ml_risk_prob:.2f}
Rule-based verification results (per statutory requirement): {json.dumps(rule_results)}

Write a concise 3-5 sentence recommendation for the Procurement Officer. Name the
specific gaps or failed checks. State clearly this is decision SUPPORT, not a final
decision — the officer must make the final qualification call. Do not use markdown."""

    failed = [name.replace("_", " ") for name, result in rule_results.items() if not result.get("pass")]
    if not client:
        return (f"Evidence-based assessment for {bidder_name}: " +
                (f"review {', '.join(failed)}." if failed else "submitted document evidence passed the configured checks.") +
                " This is decision support only; an officer must make the final determination.")
    try:
        response = client.chat.completions.create(model=settings.LLM_MODEL, max_tokens=300, messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content.strip()
    except Exception:
        return (f"Evidence-based assessment for {bidder_name}: " +
                (f"review {', '.join(failed)}." if failed else "submitted document evidence passed the configured checks.") +
                " This is decision support only; an officer must make the final determination.")
