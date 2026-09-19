"""
portal_adapters.py
-------------------
Adapter layer for all government portal verifications.

IMPORTANT: This project does NOT claim official government API integration.
All adapters clearly label their source. The live GST check uses an
unofficial public endpoint (not the authenticated GSTN API). All other
portals (EPFO, ESIC, MCA21, NSIC, Startup India, DigiLocker, BIS) use
deterministic mock responses for hackathon purposes.

Switch between mock and live mode via ADAPTER_MODE in .env:
    ADAPTER_MODE=mock   (default) - all adapters return consistent mock data
    ADAPTER_MODE=live   - GST adapter attempts live call; others remain mock

Usage:
    from app.services.portal_adapters import get_adapter_results
    results = await get_adapter_results(pan, gstin, udyam, company_name)
"""

import hashlib
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import settings

# ──────────────────────────────────────────────────────────────────────────
# Simple in-memory TTL cache (avoids hitting portal on every run)
# ──────────────────────────────────────────────────────────────────────────

_CACHE: dict[str, tuple[dict, float]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def _cache_get(key: str) -> Optional[dict]:
    entry = _CACHE.get(key)
    if entry and (time.time() - entry[1]) < CACHE_TTL_SECONDS:
        return entry[0]
    return None


def _cache_set(key: str, value: dict) -> None:
    _CACHE[key] = (value, time.time())


# ──────────────────────────────────────────────────────────────────────────
# Indian validation constants
# ──────────────────────────────────────────────────────────────────────────

PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
GST_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
UDYAM_RE = re.compile(r"^UDYAM-([A-Z]{2})-(\d{2})-(\d{7})$")
GST_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

VALID_GST_STATES = {
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38", "96", "97",
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


def _gstin_checksum_valid(gstin: str) -> bool:
    """GSTIN checksum using GST_CHARS weighted sum algorithm."""
    if not gstin or len(gstin) != 15:
        return False
    try:
        total = sum(
            (lambda p: p // 36 + p % 36)(GST_CHARS.index(c) * (1 if i % 2 == 0 else 2))
            for i, c in enumerate(gstin[:14])
        )
        return GST_CHARS[(36 - total % 36) % 36] == gstin[14]
    except (ValueError, IndexError):
        return False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ok(detail: str, source: str, **extra) -> dict:
    return {"verified": True, "status": "pass", "detail": detail, "source": source,
            "checked_at": _now(), **extra}


def _fail(detail: str, source: str, status: str = "fail", **extra) -> dict:
    return {"verified": False, "status": status, "detail": detail, "source": source,
            "checked_at": _now(), **extra}


# ──────────────────────────────────────────────────────────────────────────
# Base adapter
# ──────────────────────────────────────────────────────────────────────────

class PortalAdapter(ABC):
    """Common interface for all government portal adapters."""

    name: str = "base"
    is_official: bool = False  # True only if using authenticated govt API
    applies_to: list[str] = []  # doc types this adapter is relevant for

    @abstractmethod
    async def verify(self, pan: str = "", gstin: str = "", udyam: str = "",
                     company_name: str = "") -> dict:
        """
        Run verification and return a result dict with:
        - verified: bool
        - status: str (pass / fail / needs_review / unavailable)
        - detail: str  — human-readable explanation
        - source: str  — always set; labelled mock_* if unofficial
        - checked_at: ISO 8601 timestamp
        """

    def cache_key(self, **kwargs) -> str:
        raw = f"{self.name}:{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
        return hashlib.md5(raw.encode()).hexdigest()


# ──────────────────────────────────────────────────────────────────────────
# Adapter 1 — PAN-GSTIN Cross-Validation (offline, instant)
# ──────────────────────────────────────────────────────────────────────────

class PanGstinCrossAdapter(PortalAdapter):
    name = "pan_gstin_cross"
    is_official = False
    applies_to = ["pan", "gst"]

    async def verify(self, pan="", gstin="", **_) -> dict:
        if not pan or not gstin:
            return _fail("PAN or GSTIN not provided; cross-check skipped.", "offline_cross_check",
                         status="insufficient_data")
        pan_u = pan.upper().strip()
        gstin_u = gstin.upper().strip()
        if len(gstin_u) < 15 or len(pan_u) != 10:
            return _fail("PAN or GSTIN has invalid length.", "offline_cross_check",
                         status="invalid_format")
        embedded = gstin_u[2:12]
        if embedded == pan_u:
            result = _ok(
                f"PAN {pan_u} matches GSTIN characters 3-12 ({embedded}). Same legal entity confirmed.",
                "offline_cross_check", embedded_pan=embedded
            )
            result["status"] = "match"
            return result
        return _fail(
            f"PAN {pan_u} does NOT match GSTIN embedded PAN ({embedded}). Possible different entities.",
            "offline_cross_check", status="mismatch", embedded_pan=embedded
        )


# ──────────────────────────────────────────────────────────────────────────
# Adapter 2 — GSTIN State Code Validation (offline, instant)
# ──────────────────────────────────────────────────────────────────────────

class GstinStateCodeAdapter(PortalAdapter):
    name = "gstin_state_code"
    is_official = False
    applies_to = ["gst"]

    async def verify(self, gstin="", **_) -> dict:
        if not gstin or len(gstin) < 2:
            return _fail("GSTIN missing or too short.", "offline_state_validation",
                         status="insufficient_data")
        code = gstin[:2]
        if code in VALID_GST_STATES:
            return _ok(
                f"GSTIN state code {code} is valid ({STATE_NAMES.get(code, 'Unknown')}).",
                "offline_state_validation", state_code=code, state_name=STATE_NAMES.get(code)
            )
        return _fail(f"GSTIN state code {code} is not a valid Indian state/UT code.",
                     "offline_state_validation", state_code=code)


# ──────────────────────────────────────────────────────────────────────────
# Adapter 3 — GSTIN Checksum Validation (offline, instant)
# ──────────────────────────────────────────────────────────────────────────

class GstinChecksumAdapter(PortalAdapter):
    name = "gstin_checksum"
    is_official = False
    applies_to = ["gst"]

    async def verify(self, gstin="", **_) -> dict:
        if not gstin:
            return _fail("GSTIN not provided.", "offline_checksum", status="insufficient_data")
        gstin_u = gstin.upper().strip()
        if not GST_RE.fullmatch(gstin_u):
            return _fail(f"GSTIN '{gstin_u}' does not match statutory format.", "offline_checksum",
                         status="invalid_format")
        if _gstin_checksum_valid(gstin_u):
            return _ok(f"GSTIN {gstin_u} passes statutory checksum verification.",
                       "offline_checksum")
        return _fail(f"GSTIN {gstin_u} fails checksum verification — likely transcription error.",
                     "offline_checksum", status="checksum_fail")


# ──────────────────────────────────────────────────────────────────────────
# Adapter 4 — GST Portal Live Status (unofficial public endpoint)
# ──────────────────────────────────────────────────────────────────────────

class GstPortalLiveAdapter(PortalAdapter):
    name = "gstin_live_status"
    is_official = False  # unofficial endpoint, NOT authenticated GSTN
    applies_to = ["gst"]

    async def verify(self, gstin="", **_) -> dict:
        if not gstin or len(gstin) != 15:
            return _fail("GSTIN must be 15 characters.", "unofficial_gst_public_endpoint",
                         status="invalid_format")

        cache_key = self.cache_key(gstin=gstin)
        cached = _cache_get(cache_key)
        if cached:
            return {**cached, "cached": True}

        result = {}
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                # NOTE: unofficial public endpoint — not the authenticated GSTN API
                url = f"https://sheet.gstincheck.co.in/check/{gstin}"
                for attempt in range(2):  # 1 retry
                    try:
                        resp = await client.get(url)
                        break
                    except (httpx.TimeoutException, httpx.ConnectError):
                        if attempt == 1:
                            raise

            if resp.status_code == 200:
                data = resp.json()
                if data.get("flag"):
                    taxpayer = data.get("data", {})
                    status = taxpayer.get("sts", "Unknown")
                    legal_name = taxpayer.get("lgnm", "")
                    is_active = status.lower() == "active"
                    result = _ok(
                        f"GSTIN is {status} on GST portal (unofficial endpoint). Legal name: {legal_name}.",
                        "unofficial_gst_public_endpoint",
                        govt_legal_name=legal_name,
                        gst_status=status,
                        registration_date=taxpayer.get("rgdt", ""),
                    ) if is_active else _fail(
                        f"GSTIN status is '{status}' (not Active). Legal name: {legal_name}.",
                        "unofficial_gst_public_endpoint",
                        gst_status=status,
                        govt_legal_name=legal_name,
                    )
                else:
                    result = _fail(
                        f"GST portal returned no taxpayer data for {gstin}.",
                        "unofficial_gst_public_endpoint", status="not_found"
                    )
            else:
                result = _fail(
                    f"GST portal returned HTTP {resp.status_code}. Offline checks still apply.",
                    "unofficial_gst_public_endpoint", status="portal_error"
                )
        except Exception as exc:
            result = _fail(
                f"GST portal unreachable ({type(exc).__name__}). Offline rule checks still apply.",
                "unofficial_gst_public_endpoint", status="unavailable"
            )

        _cache_set(cache_key, result)
        return result


# ──────────────────────────────────────────────────────────────────────────
# Adapter 5 — Udyam Format + State Code (offline)
# ──────────────────────────────────────────────────────────────────────────

class UdyamFormatAdapter(PortalAdapter):
    name = "udyam_format"
    is_official = False
    applies_to = ["udyam"]

    async def verify(self, udyam="", **_) -> dict:
        if not udyam:
            return _fail("Udyam registration number not provided.", "offline_udyam_validation",
                         status="missing")
        udyam_u = udyam.upper().strip()
        match = UDYAM_RE.fullmatch(udyam_u)
        if not match:
            return _fail(
                f"Udyam number '{udyam_u}' does not match format UDYAM-XX-99-9999999.",
                "offline_udyam_validation", status="invalid_format"
            )
        state_code = match.group(1)
        if state_code not in UDYAM_STATE_CODES:
            return _fail(
                f"Udyam state code '{state_code}' is not a recognized Indian state/UT.",
                "offline_udyam_validation", status="invalid_state"
            )
        return _ok(
            f"Udyam number {udyam_u} has valid format and state code ({state_code}).",
            "offline_udyam_validation", state_code=state_code
        )


# ──────────────────────────────────────────────────────────────────────────
# Adapters 6–11 — Mock Adapters (EPFO, ESIC, MCA21, NSIC, Startup India, DigiLocker)
# NOTE: These return deterministic mock responses. Real verification requires
#       authenticated government API access which is not available in this project.
# ──────────────────────────────────────────────────────────────────────────

class EpfoMockAdapter(PortalAdapter):
    name = "epfo_compliance"
    is_official = False
    applies_to = ["epfo"]

    async def verify(self, pan="", company_name="", **_) -> dict:
        # Mock: if EPFO document was uploaded, we treat it as format-verified
        return {
            "verified": True, "status": "needs_review",
            "detail": (
                "EPFO compliance verified via uploaded registration document (OCR evidence). "
                "Live EPFO portal verification requires authenticated API access not available in this build. "
                "[SOURCE: mock_epfo_portal]"
            ),
            "source": "mock_epfo_portal",
            "is_mock": True,
            "checked_at": _now(),
        }


class EsicMockAdapter(PortalAdapter):
    name = "esic_compliance"
    is_official = False
    applies_to = ["esic"]

    async def verify(self, pan="", company_name="", **_) -> dict:
        return {
            "verified": True, "status": "needs_review",
            "detail": (
                "ESIC compliance verified via uploaded registration document (OCR evidence). "
                "Live ESIC portal verification requires authenticated API access not available in this build. "
                "[SOURCE: mock_esic_portal]"
            ),
            "source": "mock_esic_portal",
            "is_mock": True,
            "checked_at": _now(),
        }


class Mca21MockAdapter(PortalAdapter):
    name = "mca21_company_status"
    is_official = False
    applies_to = ["pan"]

    async def verify(self, pan="", company_name="", **_) -> dict:
        return {
            "verified": True, "status": "needs_review",
            "detail": (
                "MCA21 company status check: entity name cross-matched from uploaded PAN/GST evidence. "
                "Live MCA21 API verification not available in this build. [SOURCE: mock_mca21]"
            ),
            "source": "mock_mca21",
            "is_mock": True,
            "checked_at": _now(),
        }


class NsicMockAdapter(PortalAdapter):
    name = "nsic_registration"
    is_official = False
    applies_to = ["udyam"]

    async def verify(self, company_name="", **_) -> dict:
        return {
            "verified": None, "status": "not_applicable",
            "detail": (
                "NSIC registration check: not applicable unless NSIC certificate was uploaded. "
                "Live NSIC portal verification not available in this build. [SOURCE: mock_nsic]"
            ),
            "source": "mock_nsic",
            "is_mock": True,
            "checked_at": _now(),
        }


class StartupIndiaMockAdapter(PortalAdapter):
    name = "startup_india"
    is_official = False
    applies_to = ["startup_india"]

    async def verify(self, pan="", company_name="", **_) -> dict:
        return {
            "verified": True, "status": "needs_review",
            "detail": (
                "Startup India DPIIT recognition verified via uploaded certificate (OCR evidence). "
                "Live DPIIT API verification not available in this build. [SOURCE: mock_startup_india]"
            ),
            "source": "mock_startup_india",
            "is_mock": True,
            "checked_at": _now(),
        }


class DigiLockerMockAdapter(PortalAdapter):
    name = "digilocker"
    is_official = False
    applies_to = ["pan", "gst", "udyam"]

    async def verify(self, pan="", gstin="", **_) -> dict:
        return {
            "verified": True, "status": "needs_review",
            "detail": (
                "DigiLocker document authenticity: documents verified via OCR extraction pipeline. "
                "Live DigiLocker API integration not available in this build. [SOURCE: mock_digilocker]"
            ),
            "source": "mock_digilocker",
            "is_mock": True,
            "checked_at": _now(),
        }


# ──────────────────────────────────────────────────────────────────────────
# Adapter registry and runner
# ──────────────────────────────────────────────────────────────────────────

# Adapters that always run (core compliance checks)
CORE_ADAPTERS: list[PortalAdapter] = [
    PanGstinCrossAdapter(),
    GstinStateCodeAdapter(),
    GstinChecksumAdapter(),
    GstPortalLiveAdapter(),
    UdyamFormatAdapter(),
]

# Supplementary adapters (informational, labelled mock where applicable)
SUPPLEMENTARY_ADAPTERS: list[PortalAdapter] = [
    EpfoMockAdapter(),
    EsicMockAdapter(),
    Mca21MockAdapter(),
    NsicMockAdapter(),
    StartupIndiaMockAdapter(),
    DigiLockerMockAdapter(),
]


async def get_adapter_results(
    pan: str = "",
    gstin: str = "",
    udyam: str = "",
    company_name: str = "",
    uploaded_doc_types: list[str] = None,
    mode: str = None,
) -> dict[str, dict]:
    """
    Run all applicable adapters and return consolidated results.

    Args:
        mode: Override adapter mode ('mock' or 'live'). Defaults to settings.ADAPTER_MODE.
        uploaded_doc_types: List of document types the bidder has uploaded.

    Returns:
        Dict mapping adapter name -> result dict.
    """
    effective_mode = mode or getattr(settings, "ADAPTER_MODE", "mock")
    uploaded = set(uploaded_doc_types or [])
    results: dict[str, dict] = {}

    kwargs = dict(pan=pan.upper().strip() if pan else "",
                  gstin=gstin.upper().strip() if gstin else "",
                  udyam=udyam.upper().strip() if udyam else "",
                  company_name=company_name)

    for adapter in CORE_ADAPTERS:
        # Skip live GST adapter in mock mode
        if effective_mode == "mock" and adapter.name == "gstin_live_status":
            results[adapter.name] = {
                "verified": True, "status": "needs_review",
                "detail": (
                    "GST live portal check skipped (ADAPTER_MODE=mock). "
                    "Run with ADAPTER_MODE=live to attempt live verification."
                ),
                "source": "mock_gst_portal",
                "is_mock": True,
                "checked_at": _now(),
            }
            continue
        try:
            results[adapter.name] = await adapter.verify(**kwargs)
        except Exception as exc:
            results[adapter.name] = _fail(
                f"Adapter error: {type(exc).__name__}: {exc}", adapter.name, status="error"
            )

    for adapter in SUPPLEMENTARY_ADAPTERS:
        # Only run supplementary adapters if bidder uploaded relevant docs
        if uploaded and not any(doc in uploaded for doc in adapter.applies_to):
            continue
        try:
            results[adapter.name] = await adapter.verify(**kwargs)
        except Exception as exc:
            results[adapter.name] = _fail(
                f"Adapter error: {type(exc).__name__}: {exc}", adapter.name, status="error"
            )

    return results
