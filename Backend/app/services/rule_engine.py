"""Deterministic verification against uploaded document evidence and published ID syntax."""
import re
from collections import Counter

PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
UDYAM_RE = re.compile(r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$")
GST_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
GST_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def valid_gstin(value: str | None) -> bool:
    if not value or not GST_RE.fullmatch(value.upper()):
        return False
    total = 0
    for index, char in enumerate(value.upper()[:14]):
        product = GST_CHARS.index(char) * (1 if index % 2 == 0 else 2)
        total += product // 36 + product % 36
    return GST_CHARS[(36 - total % 36) % 36] == value.upper()[14]


def _normalise_name(value: str | None) -> str:
    name = (value or "").lower()
    name = re.sub(r"\bprivate\s+limited\b|\bpvt\.?\s*ltd\.?\b", "privatelimited", name)
    name = re.sub(r"\blimited\b|\bltd\.?\b", "limited", name)
    return re.sub(r"[^a-z0-9]", "", name)


def run_rule_checks(bidder: dict, documents: dict, tender_requirements: list[dict] | None = None) -> dict:
    """Use only extracted file evidence and declared bidder identifiers; never fake registry status."""
    results = {}
    required_keys = {item["requirement_key"] for item in (tender_requirements or []) if item.get("mandatory")}
    required_documents = [key for key in required_keys if key in {"pan", "gst", "udyam", "epfo", "esic", "non_blacklisting", "startup_india", "oem_auth"}]
    for doc_type in required_documents:
        results[f"{doc_type}_submitted"] = {"pass": bool(documents.get(doc_type)), "detail": "Uploaded document processed." if documents.get(doc_type) else "Required document has not been uploaded."}

    pan_doc = documents.get("pan", {}).get("fields", {})
    declared_pan = (bidder.get("pan_number") or "").upper()
    extracted_pan = (pan_doc.get("pan") or pan_doc.get("document_id") or "").upper()
    if "pan" in required_keys:
        results["pan_format"] = {"pass": bool(PAN_RE.fullmatch(declared_pan)), "detail": "Declared PAN has a valid format." if PAN_RE.fullmatch(declared_pan) else "Declared PAN format is invalid or missing."}
        results["pan_document_match"] = {"pass": bool(extracted_pan and extracted_pan == declared_pan), "detail": "PAN in uploaded evidence matches bidder declaration." if extracted_pan == declared_pan and extracted_pan else "PAN could not be matched to the uploaded PAN document."}

    gst_doc = documents.get("gst", {}).get("fields", {})
    declared_gstin = (bidder.get("gstin") or "").upper()
    extracted_gstin = (gst_doc.get("gstin") or gst_doc.get("document_id") or "").upper()
    if "gst" in required_keys:
        results["gstin_format_checksum"] = {"pass": valid_gstin(declared_gstin), "detail": "Declared GSTIN passes format and checksum validation." if valid_gstin(declared_gstin) else "Declared GSTIN fails format or checksum validation."}
        results["gst_document_match"] = {"pass": bool(extracted_gstin and extracted_gstin == declared_gstin), "detail": "GSTIN in uploaded evidence matches bidder declaration." if extracted_gstin == declared_gstin and extracted_gstin else "GSTIN could not be matched to the uploaded GST certificate."}

    udyam_doc = documents.get("udyam", {}).get("fields", {})
    declared_udyam = (bidder.get("udyam_number") or "").upper()
    extracted_udyam = (udyam_doc.get("udyam_number") or udyam_doc.get("document_id") or "").upper()
    if "udyam" in required_keys:
        results["udyam_format"] = {"pass": bool(UDYAM_RE.fullmatch(declared_udyam)), "detail": "Declared Udyam number has a valid format." if UDYAM_RE.fullmatch(declared_udyam) else "Declared Udyam number format is invalid or missing."}
        results["udyam_document_match"] = {"pass": bool(extracted_udyam and extracted_udyam == declared_udyam), "detail": "Udyam number matches uploaded evidence." if extracted_udyam == declared_udyam and extracted_udyam else "Udyam number could not be matched to uploaded evidence."}

    expected_values = {
        item.get("requirement_key"): (item.get("source_evidence") or "").upper()
        for item in (tender_requirements or [])
        if item.get("requirement_key") in {"expected_pan", "expected_gstin", "expected_udyam_number", "expected_legal_name"}
    }
    for requirement_key, profile_key, extracted_value, label in [
        ("expected_pan", "pan_number", extracted_pan, "PAN"),
        ("expected_gstin", "gstin", extracted_gstin, "GSTIN"),
        ("expected_udyam_number", "udyam_number", extracted_udyam, "Udyam registration number"),
    ]:
        expected = expected_values.get(requirement_key)
        if expected:
            declared = (bidder.get(profile_key) or "").upper()
            matches = declared == expected and extracted_value == expected
            results[f"tender_{requirement_key}_match"] = {
                "pass": matches,
                "detail": f"Tender-required {label} matches the bidder declaration and uploaded evidence." if matches else f"Tender requires {label} '{expected}', but the bidder declaration or uploaded evidence differs.",
            }
    names = [(kind, name) for kind, data in documents.items() if (name := data.get("fields", {}).get("legal_name"))]
    normalized = [(kind, original, _normalise_name(original)) for kind, original in names]
    expected_legal_name = expected_values.get("expected_legal_name")
    if expected_legal_name:
        profile_matches_tender = _normalise_name(bidder.get("company_name")) == _normalise_name(expected_legal_name)
        extracted_names_match_tender = bool(normalized) and all(
            value == _normalise_name(expected_legal_name) for _, _, value in normalized
        )
        results["tender_expected_legal_name_match"] = {
            "pass": profile_matches_tender and extracted_names_match_tender,
            "detail": "Tender-required legal entity matches the bidder profile and document evidence." if profile_matches_tender and extracted_names_match_tender else f"Tender requires legal entity '{expected_legal_name}', but the bidder profile or document evidence differs.",
        }
    if normalized:
        consensus = Counter(value for _, _, value in normalized).most_common(1)[0][0]
        mismatches = [kind for kind, _, value in normalized if value != consensus]
        consensus_name = next(original for _, original, value in normalized if value == consensus)
        results["legal_name_consistency"] = {"pass": not mismatches, "detail": "All extracted document legal names are consistent." if not mismatches else f"Document legal-name variation in: {', '.join(mismatches)}. Evidence consensus: {consensus_name}."}
        profile_matches = _normalise_name(bidder.get("company_name")) == consensus
        results["bidder_profile_name_match"] = {"pass": profile_matches, "detail": "Bidder profile name matches document evidence." if profile_matches else f"Bidder profile name does not match document-evidence entity '{consensus_name}'. Update the bidder profile or request clarification."}
    else:
        results["legal_name_consistency"] = {"pass": False, "detail": "No legal name could be extracted from submitted documents."}
    results["registry_confirmation"] = {"pass": False, "detail": "Not performed: no authorised GSTN/NSDL/Udyam/EPFO/ESIC registry integration is configured."}
    return results


def rule_based_score(results: dict) -> float:
    scored = [result for key, result in results.items() if key != "registry_confirmation"]
    return round(100 * sum(bool(result["pass"]) for result in scored) / len(scored), 1) if scored else 0.0
