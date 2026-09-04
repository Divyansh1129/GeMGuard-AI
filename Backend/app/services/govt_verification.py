"""
govt_verification.py
---------------------
Live verification adapters for Indian government databases.

1. PAN-GSTIN Cross-Validation (offline, instant)
2. GSTIN Status via GST Portal public search
3. GSTIN State Code validation
4. Udyam Registration check (format + state validation)

These adapters add field_checks with source="govt_portal" so the UI can
distinguish between offline rule checks and live govt verification.
"""

import re
import httpx
from datetime import datetime, timezone

# Indian state codes for GSTIN validation (first 2 digits)
VALID_STATE_CODES = {
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38",
    "96", "97",  # special: foreign territories, UN bodies
}

STATE_NAMES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "25": "Daman & Diu", "26": "Dadra & Nagar Haveli",
    "27": "Maharashtra", "28": "Andhra Pradesh (Old)", "29": "Karnataka",
    "30": "Goa", "31": "Lakshadweep", "32": "Kerala",
    "33": "Tamil Nadu", "34": "Puducherry", "35": "Andaman & Nicobar",
    "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
    "96": "Foreign Country", "97": "Other Territory",
}

UDYAM_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CT", "DD", "DL", "GA",
    "GJ", "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD", "MH",
    "ML", "MN", "MP", "MZ", "NL", "OR", "PB", "PY", "RJ", "SK",
    "TN", "TS", "TR", "UK", "UP", "WB",
}


def verify_pan_gstin_cross(pan: str, gstin: str) -> dict:
    """
    Characters 3-12 of a valid GSTIN must equal the PAN.
    This is a free, instant, offline check - no API needed.

    GSTIN format: SS PPPPP9999P E Z C
                  ^^ ^^^^^^^^^^
                  state  PAN (chars 3-12, 0-indexed 2:12)
    """
    result = {
        "source": "pan_gstin_crosscheck",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    if not pan or not gstin or len(gstin) < 15 or len(pan) != 10:
        result["verified"] = False
        result["status"] = "insufficient_data"
        result["detail"] = "PAN or GSTIN is missing or has invalid length."
        return result

    pan_upper = pan.upper().strip()
    gstin_upper = gstin.upper().strip()
    embedded_pan = gstin_upper[2:12]

    if embedded_pan == pan_upper:
        result["verified"] = True
        result["status"] = "match"
        result["detail"] = f"PAN {pan_upper} matches GSTIN characters 3-12 ({embedded_pan}). Same legal entity confirmed."
        result["embedded_pan"] = embedded_pan
    else:
        result["verified"] = False
        result["status"] = "mismatch"
        result["detail"] = f"PAN {pan_upper} does NOT match GSTIN embedded PAN ({embedded_pan}). These may belong to different entities."
        result["embedded_pan"] = embedded_pan

    return result


def verify_gstin_state_code(gstin: str) -> dict:
    """Validate that the first 2 digits of GSTIN are a real Indian state code."""
    result = {
        "source": "gstin_state_validation",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    if not gstin or len(gstin) < 2:
        result["verified"] = False
        result["status"] = "insufficient_data"
        result["detail"] = "GSTIN is missing or too short."
        return result

    state_code = gstin[:2]
    if state_code in VALID_STATE_CODES:
        state_name = STATE_NAMES.get(state_code, "Unknown")
        result["verified"] = True
        result["status"] = "valid"
        result["state_code"] = state_code
        result["state_name"] = state_name
        result["detail"] = f"GSTIN state code {state_code} is valid ({state_name})."
    else:
        result["verified"] = False
        result["status"] = "invalid"
        result["state_code"] = state_code
        result["detail"] = f"GSTIN state code {state_code} is not a valid Indian state/UT code."

    return result


async def verify_gstin_status(gstin: str) -> dict:
    """
    Query the public GST portal to check if a GSTIN is Active.
    Uses a public endpoint that returns taxpayer status and legal name.

    Falls back gracefully if the portal is unavailable.
    """
    result = {
        "source": "gst_portal",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "gstin": gstin,
    }

    if not gstin or len(gstin) != 15:
        result["verified"] = False
        result["status"] = "invalid_format"
        result["detail"] = "GSTIN must be exactly 15 characters."
        return result

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Public GST search endpoint (no auth required)
            url = f"https://sheet.gstincheck.co.in/check/{gstin}"
            resp = await client.get(url)

            if resp.status_code == 200:
                data = resp.json()
                if data.get("flag"):
                    taxpayer = data.get("data", {})
                    status = taxpayer.get("sts", "Unknown")
                    legal_name = taxpayer.get("lgnm", "")
                    trade_name = taxpayer.get("tradeNam", "")
                    reg_date = taxpayer.get("rgdt", "")

                    result["verified"] = status.lower() == "active"
                    result["status"] = status.lower()
                    result["govt_legal_name"] = legal_name
                    result["govt_trade_name"] = trade_name
                    result["registration_date"] = reg_date
                    result["detail"] = (
                        f"GSTIN is {status} on GST portal. Legal name: {legal_name}."
                        if result["verified"]
                        else f"GSTIN status is '{status}' (not Active). Legal name: {legal_name}."
                    )
                    result["raw_response"] = taxpayer
                    return result

            # Portal returned non-200 or no flag
            result["verified"] = False
            result["status"] = "portal_error"
            result["detail"] = f"GST portal returned status {resp.status_code}. Verification pending."

    except Exception as exc:
        # Network error, timeout, etc. - degrade gracefully
        result["verified"] = False
        result["status"] = "unavailable"
        result["detail"] = f"GST portal unreachable: {type(exc).__name__}. Offline checks still apply."

    return result


def verify_udyam_format(udyam_number: str) -> dict:
    """
    Validate Udyam registration number format and state code.
    Format: UDYAM-XX-99-9999999 where XX is a valid state code.
    """
    result = {
        "source": "udyam_format_validation",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    if not udyam_number:
        result["verified"] = False
        result["status"] = "missing"
        result["detail"] = "Udyam registration number is missing."
        return result

    udyam_upper = udyam_number.upper().strip()
    pattern = re.compile(r"^UDYAM-([A-Z]{2})-(\d{2})-(\d{7})$")
    match = pattern.fullmatch(udyam_upper)

    if not match:
        result["verified"] = False
        result["status"] = "invalid_format"
        result["detail"] = f"Udyam number '{udyam_upper}' does not match expected format UDYAM-XX-99-9999999."
        return result

    state_code = match.group(1)
    if state_code not in UDYAM_STATE_CODES:
        result["verified"] = False
        result["status"] = "invalid_state"
        result["detail"] = f"Udyam state code '{state_code}' is not a recognized Indian state/UT."
        return result

    result["verified"] = True
    result["status"] = "valid"
    result["state_code"] = state_code
    result["detail"] = f"Udyam number {udyam_upper} has valid format and state code ({state_code})."
    return result


async def run_all_govt_checks(pan: str, gstin: str, udyam: str) -> dict:
    """
    Run all government verification checks and return consolidated results.
    Called once per compliance run.
    """
    results = {}

    # 1. PAN-GSTIN cross-validation (instant, offline)
    if pan and gstin:
        results["pan_gstin_cross"] = verify_pan_gstin_cross(pan, gstin)

    # 2. GSTIN state code validation (instant, offline)
    if gstin:
        results["gstin_state_code"] = verify_gstin_state_code(gstin)

    # 3. Live GSTIN status check (async, govt portal)
    if gstin and len(gstin) == 15:
        results["gstin_live_status"] = await verify_gstin_status(gstin)

    # 4. Udyam format + state validation (instant, offline)
    if udyam:
        results["udyam_format"] = verify_udyam_format(udyam)

    return results
