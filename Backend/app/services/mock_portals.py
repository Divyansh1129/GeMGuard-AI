"""
mock_portals.py
----------------
WHY THIS FILE EXISTS:
Real government verification APIs (Udyam, GSTN, PAN/Income-Tax, EPFO, ESIC) are NOT
publicly available — they require signed MoUs / GSP licenses only registered
entities (banks, GSPs) can get. You cannot get real access in a hackathon.

What real integration looks like (for your pitch, not code you'll run):
  - GSTN Search Taxpayer API  -> via a licensed GST Suvidha Provider (GSP)
  - Udyam Verification        -> no public API; MSME ministry restricted
  - PAN Verification          -> NSDL/Protean eGov API, restricted to authorized entities
  - EPFO/ESIC compliance      -> Employer compliance data, not publicly exposed
  - DigiLocker                -> DOES have a public Partner API
                                  (https://partners.digilocker.gov.in) — the one real
                                  integration you could actually register for even in
                                  a hackathon.

STRATEGY:
Build this file as a clean abstraction layer — each function simulates what the real
API response would look like. When a real integration becomes available, you only
change the inside of these functions; nothing else in the app needs to change.
This is your "integration-ready" story for judges.
"""

import random


def verify_udyam(udyam_number: str) -> dict:
    """Simulates Udyam Registration portal lookup."""
    if not udyam_number or len(udyam_number) < 10:
        return {"valid": False, "status": "not_found", "reason": "Invalid Udyam number format"}
    seed = sum(ord(c) for c in udyam_number)
    random.seed(seed)
    valid = random.random() > 0.15
    return {
        "valid": valid,
        "status": "active" if valid else "expired",
        "category": random.choice(["Micro", "Small", "Medium"]),
        "registration_date": "2021-03-15",
        "source": "MOCK: simulated Udyam portal response"
    }


def verify_gstn(gstin: str) -> dict:
    """Simulates GSTN Search Taxpayer API response."""
    if not gstin or len(gstin) != 15:
        return {"valid": False, "status": "invalid_format"}
    seed = sum(ord(c) for c in gstin)
    random.seed(seed)
    active = random.random() > 0.08
    returns_filed_pct = round(random.uniform(60, 100), 1)
    return {
        "valid": True,
        "status": "active" if active else "cancelled",
        "returns_filed_pct_last_12m": returns_filed_pct,
        "source": "MOCK: simulated GSTN response"
    }


def verify_pan(pan_number: str) -> dict:
    """Simulates PAN/Income-Tax compliance verification."""
    if not pan_number or len(pan_number) != 10:
        return {"valid": False}
    seed = sum(ord(c) for c in pan_number)
    random.seed(seed)
    return {
        "valid": True,
        "itr_filed_last_year": random.random() > 0.12,
        "defaulter_flag": random.random() < 0.07,
        "source": "MOCK: simulated PAN/IT department response"
    }


def verify_epfo_esic(entity_id: str, applicable: bool) -> dict:
    """Simulates EPFO/ESIC employer compliance check."""
    if not applicable:
        return {"applicable": False, "compliant": True}
    seed = sum(ord(c) for c in entity_id) if entity_id else 0
    random.seed(seed)
    return {
        "applicable": True,
        "compliant": random.random() > 0.15,
        "source": "MOCK: simulated EPFO/ESIC employer portal response"
    }


def check_blacklist_debarment(pan_number: str) -> dict:
    """Simulates GeM's own blacklist/debarment registry lookup."""
    seed = sum(ord(c) for c in pan_number) if pan_number else 0
    random.seed(seed + 999)
    return {
        "blacklisted": random.random() < 0.04,
        "debarred": random.random() < 0.02,
        "source": "MOCK: simulated GeM debarment registry"
    }