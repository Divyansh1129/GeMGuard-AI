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
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def extract_fields(doc_type: str, raw_text: str) -> dict:
    """Ask the LLM to pull structured fields out of messy OCR text."""
    prompt = f"""You are extracting structured data from an Indian government document.
Document type: {doc_type}
Raw OCR text:
---
{raw_text[:4000]}
---
Extract the relevant fields (e.g. registration number, name, dates, GSTIN, PAN,
validity/expiry date, category) as a flat JSON object. If a field is not present,
omit it. Respond with ONLY valid JSON, no other text, no markdown fences."""

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_parse_error": True, "_raw_response": raw}


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

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()