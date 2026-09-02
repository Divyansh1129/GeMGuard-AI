"""One reconciled source of truth for evidence checks and document outcomes."""
import re
from collections import Counter

PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
UDYAM_RE = re.compile(r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$")
GST_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
GST_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def valid_gstin(value):
    if not value or not GST_RE.fullmatch(value.upper()): return False
    total = sum((lambda p: p // 36 + p % 36)(GST_CHARS.index(c) * (1 if i % 2 == 0 else 2)) for i, c in enumerate(value.upper()[:14]))
    return GST_CHARS[(36 - total % 36) % 36] == value.upper()[14]


def normalise_name(value):
    name = (value or "").lower()
    name = re.sub(r"\b(private\s+limited|pvt\.?\s*ltd\.?|limited\s+liability\s+partnership|llp|limited|ltd\.?)\b", "", name)
    return re.sub(r"[^a-z0-9]", "", name)


def _check(results, key, applies_to, field_name, status, reason, compared_against=None, required=True):
    """Every rule declares its affected document types here; callers never infer from its key."""
    results[key] = {"pass": status == "pass", "status": status, "detail": reason,
                    "applies_to": applies_to, "field_name": field_name,
                    "compared_against": compared_against, "required": required}


def run_rule_checks(bidder, documents, tender_requirements=None):
    results, requirements = {}, tender_requirements or []
    required = {item["requirement_key"] for item in requirements if item.get("mandatory")}
    document_types = list(documents)
    for kind in required & {"pan","gst","udyam","epfo","esic","non_blacklisting","startup_india","oem_auth"}:
        _check(results, f"{kind}_submitted", [kind], "document", "pass" if documents.get(kind) else "fail", "Uploaded document processed." if documents.get(kind) else "Required document has not been uploaded.")
    checks = [("pan", "pan_number", "pan", PAN_RE, "PAN"), ("gst", "gstin", "gstin", valid_gstin, "GSTIN"), ("udyam", "udyam_number", "udyam_number", UDYAM_RE.fullmatch, "Udyam number")]
    for kind, profile_key, field, validator, label in checks:
        if kind not in required: continue
        declared = (bidder.get(profile_key) or "").upper()
        extracted = (documents.get(kind, {}).get("fields", {}).get(field) or documents.get(kind, {}).get("fields", {}).get("document_id") or "").upper()
        valid = bool(validator(declared))
        _check(results, f"{kind}_format", [kind], field, "pass" if valid else "fail", f"Declared {label} has a valid format." if valid else f"Declared {label} format or checksum is invalid.", "bidder profile")
        matches = bool(extracted and extracted == declared)
        _check(results, f"{kind}_document_match", [kind], field, "pass" if matches else "fail", f"{label} in uploaded evidence matches bidder declaration." if matches else f"{label} could not be matched to uploaded evidence.", "bidder profile")
    expected = {i.get("requirement_key"):(i.get("source_evidence") or "").upper() for i in requirements}
    for kind, profile_key, field, label in [("pan","pan_number","pan","PAN"),("gst","gstin","gstin","GSTIN"),("udyam","udyam_number","udyam_number","Udyam number")]:
        target = expected.get(f"expected_{'gstin' if kind == 'gst' else 'udyam_number' if kind == 'udyam' else 'pan'}")
        if target:
            extracted=(documents.get(kind,{}).get("fields",{}).get(field) or documents.get(kind,{}).get("fields",{}).get("document_id") or "").upper()
            passed=(bidder.get(profile_key) or "").upper()==target and extracted==target
            _check(results, f"tender_expected_{kind}_match", [kind], field, "pass" if passed else "fail", f"Tender-required {label} matches profile and evidence." if passed else f"Tender-required {label} differs from profile or evidence.", "tender")
    names={kind:data.get("fields",{}).get("legal_name") for kind,data in documents.items() if data.get("fields",{}).get("legal_name")}
    consensus=Counter(normalise_name(v) for v in names.values()).most_common(1)
    expected_name=expected.get("expected_legal_name")
    for kind in document_types:
        name=names.get(kind)
        if not name:
            _check(results, f"legal_name_consistency_{kind}", [kind], "legal_name", "needs_review", "Legal name was not extracted; cross-document comparison cannot run.", "other uploaded documents")
            continue
        consistent=bool(consensus) and normalise_name(name)==consensus[0][0]
        _check(results, f"legal_name_consistency_{kind}", [kind], "legal_name", "pass" if consistent else "fail", "Legal name is consistent with uploaded evidence." if consistent else "Legal name differs from the document-evidence consensus.", "other uploaded documents")
        if expected_name:
            target_ok=normalise_name(name)==normalise_name(expected_name) and normalise_name(bidder.get("company_name"))==normalise_name(expected_name)
            _check(results, f"tender_expected_legal_name_{kind}", [kind], "legal_name", "pass" if target_ok else "fail", "Tender legal entity matches profile and evidence." if target_ok else "Tender legal entity differs from profile or evidence.", "tender")
    return results


def build_document_results(documents, rules):
    output=[]
    for kind, document in documents.items():
        checks=[{"field_name":r["field_name"],"status":r["status"],"reason":r["detail"],"compared_against":r["compared_against"],"required":r["required"],"rule_key":key} for key,r in rules.items() if kind in r["applies_to"]]
        if not checks: checks=[{"field_name":"document","status":"needs_review","reason":"No compliance checks apply yet; recompute required.","compared_against":None,"required":True,"rule_key":"unverified"}]
        status="fail" if any(c["status"]=="fail" and c["required"] for c in checks) else "needs_review" if any(c["status"]=="needs_review" for c in checks) else "pass"
        score=0 if status=="fail" else 50 if status=="needs_review" else 100
        output.append({"document_id":document["id"],"document_type":kind,"extraction_confidence":document.get("fields",{}).get("confidence"),"extracted_fields":document.get("fields",{}),"field_checks":checks,"overall_status":status,"overall_score":score})
    return output


def rule_based_score(results):
    return round(100 * sum(r["status"] == "pass" for r in results) / len(results), 1) if results else 0.0
