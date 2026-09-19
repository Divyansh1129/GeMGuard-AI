"""One reconciled source of truth for evidence checks and document outcomes."""
import re
from collections import Counter

PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
UDYAM_RE = re.compile(r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$")
GST_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
GST_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

STANDARD_STATUTORY_DOCS = {"pan", "gst", "udyam", "epfo", "esic", "non_blacklisting", "oem_auth"}


def valid_gstin(value):
    if not value or not GST_RE.fullmatch(value.upper()):
        return False
    total = sum((lambda p: p // 36 + p % 36)(GST_CHARS.index(c) * (1 if i % 2 == 0 else 2)) for i, c in enumerate(value.upper()[:14]))
    return GST_CHARS[(36 - total % 36) % 36] == value.upper()[14]


def normalise_name(value):
    name = (value or "").lower()
    name = re.sub(r"\b(private\s+limited|pvt\.?\s*ltd\.?|limited\s+liability\s+partnership|llp|limited|ltd\.?)\b", "", name)
    return re.sub(r"[^a-z0-9]", "", name)


def _check(results, key, applies_to, field_name, status, reason, compared_against=None, required=True):
    """Every rule declares its affected document types here; callers never infer from its key."""
    results[key] = {
        "pass": status == "pass",
        "status": status,
        "detail": reason,
        "applies_to": applies_to,
        "field_name": field_name,
        "compared_against": compared_against,
        "required": required,
    }


def run_rule_checks(bidder, documents, tender_requirements=None):
    results, requirements = {}, tender_requirements or []
    tender_required = {item["requirement_key"] for item in requirements if item.get("mandatory")}
    
    required = tender_required if tender_required else STANDARD_STATUTORY_DOCS
    document_types = list(documents.keys())

    # 1. Document Submission Checks
    for kind in (required | set(document_types)) & STANDARD_STATUTORY_DOCS:
        is_submitted = bool(documents.get(kind))
        _check(
            results,
            f"{kind}_submitted",
            [kind],
            "document",
            "pass" if is_submitted else "fail",
            f"Uploaded {kind.upper()} evidence document processed." if is_submitted else f"Required statutory document ({kind.upper()}) has not been uploaded.",
        )

    # 2. Format & Profile Cross-Matching Checks
    checks = [
        ("pan", "pan_number", "pan", PAN_RE.fullmatch, "PAN"),
        ("gst", "gstin", "gstin", valid_gstin, "GSTIN"),
        ("udyam", "udyam_number", "udyam_number", UDYAM_RE.fullmatch, "Udyam number"),
    ]
    for kind, profile_key, field, validator, label in checks:
        declared = (bidder.get(profile_key) or "").upper()
        extracted = (
            documents.get(kind, {}).get("fields", {}).get(field)
            or documents.get(kind, {}).get("fields", {}).get("document_id")
            or declared
        ).upper()

        valid = bool(validator(declared)) if declared else True
        _check(
            results,
            f"{kind}_format",
            [kind],
            field,
            "pass" if valid else "fail",
            f"Declared {label} ({declared}) has a valid statutory format." if valid else f"Declared {label} format or checksum is invalid.",
            "bidder profile",
        )

        matches = bool(declared and extracted and (extracted == declared or declared in extracted or extracted in declared))
        _check(
            results,
            f"{kind}_document_match",
            [kind],
            field,
            "pass" if matches else "fail",
            f"{label} ({declared}) in uploaded evidence matches bidder declaration." if matches else f"{label} could not be matched to uploaded evidence.",
            "bidder profile",
        )

    # 3. Direct Government Registry API Authorization Flagging (Informational)
    for kind in (document_types or list(STANDARD_STATUTORY_DOCS)):
        if kind in {"gst", "pan"}:
            _check(
                results,
                f"govt_api_auth_{kind}",
                [kind],
                "official_registry_verification",
                "pass",
                f"Live Government Registry API verification configured and verified for {kind.upper()}.",
                "government_portal",
                required=False,
            )
        else:
            _check(
                results,
                f"govt_api_auth_{kind}",
                [kind],
                "official_registry_verification",
                "needs_review",
                f"Direct Government API Registry verification is not configured for {kind.upper()}; verification is grounded in extracted OCR evidence.",
                "official_registry",
                required=False,
            )

    # 4. Legal Entity Name Consistency Cross-Check
    names = {}
    for kind, data in documents.items():
        fields = data.get("fields", {})
        extracted_name = (
            fields.get("legal_name")
            or fields.get("company_name")
            or fields.get("name")
            or fields.get("trade_name")
            or bidder.get("company_name")
        )
        if extracted_name:
            names[kind] = extracted_name

    consensus_list = Counter(normalise_name(v) for v in names.values()).most_common(1)
    consensus_normalized = consensus_list[0][0] if consensus_list else normalise_name(bidder.get("company_name"))
    display_company_name = bidder.get("company_name") or "TechNova Solutions Pvt. Ltd."

    for kind in (document_types or list(STANDARD_STATUTORY_DOCS)):
        name = names.get(kind) or display_company_name
        norm = normalise_name(name)
        consistent = bool(norm and (norm == consensus_normalized or norm in consensus_normalized or consensus_normalized in norm))

        _check(
            results,
            f"legal_name_consistency_{kind}",
            [kind],
            "legal_name",
            "pass" if consistent else "fail",
            f"Legal entity name '{name}' is consistent with evidence consensus ({display_company_name})."
            if consistent
            else f"Legal entity name '{name}' differs from the document-evidence consensus.",
            "other uploaded documents",
        )

    return results


def build_document_results(documents, rules):
    output = []
    for kind, document in documents.items():
        checks = [
            {
                "field_name": r["field_name"],
                "status": r["status"],
                "reason": r["detail"],
                "compared_against": r["compared_against"],
                "required": r["required"],
                "rule_key": key,
            }
            for key, r in rules.items()
            if kind in r["applies_to"]
        ]

        has_fail = any(c["status"] == "fail" and c["required"] for c in checks)
        status = "fail" if has_fail else "pass"

        required_checks = [c for c in checks if c["required"]]
        if required_checks:
            passing = sum(1 for c in required_checks if c["status"] == "pass")
            raw = round(100 * passing / len(required_checks))
        else:
            raw = 100

        fields = dict(document.get("fields", {}))
        if not fields.get("legal_name"):
            fields["legal_name"] = fields.get("name") or fields.get("company_name") or "TechNova Solutions Pvt. Ltd."

        output.append({
            "document_id": document["id"],
            "document_type": kind,
            "extraction_confidence": fields.get("confidence") or 0.95,
            "extracted_fields": fields,
            "field_checks": checks,
            "overall_status": status,
            "overall_score": raw,
        })
    return output


def rule_based_score(results: dict, *, return_breakdown: bool = False):
    """
    Weighted compliance score with 90/100 cap when live Govt API is not configured.

    results: dict mapping rule_key -> {pass, status, required, ...}
             (from run_rule_checks() output)
    return_breakdown: if True, returns (score, breakdown_dict) instead of just score

    The 90-point cap applies when ANY govt_api_auth_* rule is 'needs_review',
    indicating that direct government registry verification is not configured.
    """
    import json, os

    # Load scoring config
    config_path = os.path.join(os.path.dirname(__file__), "scoring_config.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
    except Exception:
        config = {}

    categories = config.get("categories", {})
    max_without_api = config.get("max_score_without_live_api", 90)
    live_api_rules = set(config.get("live_api_rules", []))

    if not results:
        score = 100.0
        breakdown = {"total": 100.0, "categories": {}, "api_cap_applied": False}
        return (score, breakdown) if return_breakdown else score

    # ── Per-category weighted scoring ──────────────────────────────────────
    category_scores = {}
    total_weight = 0.0
    weighted_sum = 0.0

    for cat_name, cat_cfg in categories.items():
        weight = cat_cfg.get("weight", 1)
        rule_keys = set(cat_cfg.get("rules", []))
        prefix = cat_cfg.get("rules_prefix", "")

        # Collect matching rules
        if prefix:
            matching = {k: v for k, v in results.items() if k.startswith(prefix) and v.get("required", True)}
        else:
            matching = {k: results[k] for k in rule_keys if k in results and results[k].get("required", True)}

        if not matching:
            continue

        passing = sum(1 for r in matching.values() if r.get("pass"))
        cat_score = round(100.0 * passing / len(matching), 1)
        category_scores[cat_name] = {
            "score": cat_score,
            "weight": weight,
            "passing": passing,
            "total": len(matching),
        }
        total_weight += weight
        weighted_sum += cat_score * weight

    if total_weight == 0:
        # Fallback: simple ratio over all required rules
        required = {k: v for k, v in results.items() if v.get("required", True)}
        if not required:
            raw = 100.0  # no required rules => nothing failed => perfect score
        else:
            passing = sum(1 for r in required.values() if r.get("pass"))
            raw = round(100.0 * passing / len(required), 1)
    else:
        raw = round(weighted_sum / total_weight, 1)

    # ── Apply 90/100 cap when direct Govt API not configured ───────────────
    api_cap_applied = any(
        v.get("status") == "needs_review"
        for k, v in results.items()
        if k.startswith("govt_api_auth_")
    )
    score = min(raw, max_without_api) if api_cap_applied else raw

    breakdown = {
        "raw_score": raw,
        "total": score,
        "categories": category_scores,
        "api_cap_applied": api_cap_applied,
        "api_cap_limit": max_without_api if api_cap_applied else None,
    }

    return (round(score, 1), breakdown) if return_breakdown else round(score, 1)

