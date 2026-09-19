"""
security_utils.py
-------------------
Security and robustness helpers for GeMGuard AI:
1. Masking utilities for PII / Statutory IDs (PAN, GSTIN)
2. MIME magic-byte file header validation
"""
import os
import re

# ──────────────────────────────────────────────────────────────────────────
# Masking Utilities
# ──────────────────────────────────────────────────────────────────────────

def mask_pan(pan: str) -> str:
    """
    Mask a 10-char PAN for display / logging.
    Format: ABCDE1234F -> ABCDE****F
    """
    if not pan or len(pan) != 10:
        return pan or ""
    return f"{pan[:5]}****{pan[-1]}"


def mask_gstin(gstin: str) -> str:
    """
    Mask a 15-char GSTIN for display / logging.
    Format: 27AABCT1234E1ZP -> 27AABCT****E1ZP
    """
    if not gstin or len(gstin) != 15:
        return gstin or ""
    return f"{gstin[:7]}****{gstin[-4:]}"


def sanitize_dict_for_logging(data: dict) -> dict:
    """Recursively mask sensitive fields in dicts before logging."""
    masked = {}
    for k, v in data.items():
        if isinstance(v, dict):
            masked[k] = sanitize_dict_for_logging(v)
        elif k in ("pan", "pan_number", "pan_val") and isinstance(v, str):
            masked[k] = mask_pan(v)
        elif k in ("gstin", "gstin_number", "gstin_val") and isinstance(v, str):
            masked[k] = mask_gstin(v)
        else:
            masked[k] = v
    return masked


# ──────────────────────────────────────────────────────────────────────────
# File Validation (Extension + MIME Magic Bytes)
# ──────────────────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

# Magic byte signatures
MAGIC_SIGNATURES = [
    (b"%PDF", ".pdf"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"\xff\xd8\xff", ".jpg"),  # JPEG starts with FF D8 FF
]


def validate_file_content(content: bytes, filename: str) -> str:
    """
    Validate uploaded file using both extension and magic byte signatures.
    Returns detected extension if valid, or raises ValueError if invalid.
    """
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension '{ext}'. Only PDF, PNG, JPG, JPEG allowed.")

    if len(content) < 4:
        raise ValueError("File content is too short to be valid.")

    # Check magic bytes
    magic_matched = False
    for signature, sig_ext in MAGIC_SIGNATURES:
        if content.startswith(signature):
            magic_matched = True
            break

    if not magic_matched:
        raise ValueError(
            f"File '{filename}' header does not match expected format (PDF/PNG/JPG). "
            "File may be corrupted or disguised."
        )

    return ext
