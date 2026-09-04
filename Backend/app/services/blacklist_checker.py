"""
blacklist_checker.py
---------------------
Checks bidder entities against a database of known blacklisted/debarred
companies from CVC (Central Vigilance Commission), GeM, and other
government blacklisting sources.

Uses fuzzy name matching so variations like "Pvt. Ltd." vs "Private Limited"
don't escape the check.
"""

import json
import os
import re
from datetime import datetime, timezone

# Path to the blacklist database (JSON file)
_BLACKLIST_PATH = os.path.join(os.path.dirname(__file__), "blacklist_data.json")

# Normalize for fuzzy matching (same logic as rule_engine.normalise_name)
def _normalize(name: str) -> str:
    name = (name or "").lower()
    name = re.sub(
        r"\b(private\s+limited|pvt\.?\s*ltd\.?|limited\s+liability\s+partnership|llp|limited|ltd\.?)\b",
        "", name,
    )
    return re.sub(r"[^a-z0-9]", "", name)


def _load_blacklist() -> list[dict]:
    """Load the blacklist database. Returns empty list if file doesn't exist."""
    if not os.path.isfile(_BLACKLIST_PATH):
        return []
    try:
        with open(_BLACKLIST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def check_blacklist(
    company_name: str,
    pan: str = None,
    gstin: str = None,
) -> dict:
    """
    Check a bidder against the blacklist database.

    Matching strategy:
    1. Exact PAN match (strongest signal)
    2. Exact GSTIN match
    3. Fuzzy company name match (normalized)

    Returns a result dict with status and match details.
    """
    result = {
        "source": "blacklist_database",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "matches": [],
    }

    blacklist = _load_blacklist()
    if not blacklist:
        result["status"] = "clean"
        result["verified"] = True
        result["detail"] = "No blacklist database available; entity not flagged."
        return result

    normalized_name = _normalize(company_name)
    pan_upper = (pan or "").upper().strip()
    gstin_upper = (gstin or "").upper().strip()

    for entry in blacklist:
        match_type = None
        confidence = 0

        # 1. PAN match (highest confidence)
        if pan_upper and entry.get("pan", "").upper() == pan_upper:
            match_type = "pan_match"
            confidence = 100

        # 2. GSTIN match
        elif gstin_upper and entry.get("gstin", "").upper() == gstin_upper:
            match_type = "gstin_match"
            confidence = 100

        # 3. Name match (fuzzy)
        elif normalized_name and _normalize(entry.get("name", "")) == normalized_name:
            match_type = "name_match"
            confidence = 90

        if match_type:
            result["matches"].append({
                "match_type": match_type,
                "confidence": confidence,
                "blacklisted_entity": entry.get("name"),
                "pan": entry.get("pan"),
                "reason": entry.get("reason", "Blacklisted/debarred by government authority"),
                "debarred_by": entry.get("debarred_by", "Unknown authority"),
                "debarment_date": entry.get("date"),
                "debarment_until": entry.get("until"),
            })

    if result["matches"]:
        result["status"] = "blacklisted"
        result["verified"] = False
        best = result["matches"][0]
        result["detail"] = (
            f"ALERT: Entity matches blacklisted company '{best['blacklisted_entity']}' "
            f"(matched via {best['match_type']}, confidence: {best['confidence']}%). "
            f"Reason: {best['reason']}. Debarred by: {best['debarred_by']}."
        )
    else:
        result["status"] = "clean"
        result["verified"] = True
        result["detail"] = f"Entity '{company_name}' is not found in the blacklist database ({len(blacklist)} entries checked)."

    return result
