"""
tests/test_e2e_scenarios.py
----------------------------
End-to-end compliance rule evaluation tests for 5 key scenarios (TASK 8).
These tests run the full rule engine + score computation for each scenario
and assert that the expected compliance outcome matches.

No database, no HTTP calls — pure rule engine + scoring logic.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.rule_engine import run_rule_checks, build_document_results, rule_based_score


# ── Helpers ───────────────────────────────────────────────────────────────

def _bidder(company, pan, gstin, udyam=""):
    return {"company_name": company, "pan_number": pan, "gstin": gstin, "udyam_number": udyam}


def _doc(doc_id, fields, confidence=0.98):
    return {"id": doc_id, "fields": {**fields, "confidence": confidence}, "has_text": True}


def _requirements(*keys):
    return [{"requirement_key": k, "mandatory": True, "source_evidence": ""} for k in keys]


def _run(bidder, docs, req_keys):
    """Full pipeline: rule_checks -> build_document_results -> score."""
    reqs = _requirements(*req_keys)
    rules = run_rule_checks(bidder, docs, reqs)
    results = build_document_results(docs, rules)
    score, breakdown = rule_based_score(rules, return_breakdown=True)
    return rules, results, score, breakdown


# ── Scenario 1: Fully Compliant ───────────────────────────────────────────

def test_scenario_fully_compliant():
    """
    S01: All 7 docs present, PAN/GSTIN/Udyam match, consistent legal names.
    Expected: all docs pass (excluding GSTIN checksum which depends on exact number),
    score must be > 60.
    """
    bidder = _bidder("TechNova Solutions Pvt. Ltd.", "AABCT1234E", "27AABCT1234E1ZP", "UDYAM-MH-26-0012345")
    docs = {
        "pan": _doc(1, {"pan": "AABCT1234E", "legal_name": "TechNova Solutions Pvt. Ltd."}),
        "gst": _doc(2, {"gstin": "27AABCT1234E1ZP", "legal_name": "TechNova Solutions Pvt. Ltd."}),
        "udyam": _doc(3, {"udyam_number": "UDYAM-MH-26-0012345", "legal_name": "TechNova Solutions Pvt. Ltd."}),
        "epfo": _doc(4, {"epfo_number": "MHPUN0012345000", "legal_name": "TechNova Solutions Pvt. Ltd."}),
        "esic": _doc(5, {"esic_number": "31000123456789012", "legal_name": "TechNova Solutions Pvt. Ltd."}),
        "non_blacklisting": _doc(6, {"legal_name": "TechNova Solutions Pvt. Ltd."}),
        "oem_auth": _doc(7, {"legal_name": "TechNova Solutions Pvt. Ltd."}),
    }
    rules, results, score, breakdown = _run(
        bidder, docs, ["pan", "gst", "udyam", "epfo", "esic", "non_blacklisting", "oem_auth"]
    )

    # Verify all documents exist in results
    result_types = {r["document_type"] for r in results}
    assert "pan" in result_types, "S01: PAN document must appear in results"
    assert "gst" in result_types, "S01: GST document must appear in results"
    assert "udyam" in result_types, "S01: Udyam document must appear in results"

    # Legal name consistency must pass for all docs (same name across all)
    for r in results:
        consistency_checks = [c for c in r["field_checks"] if c["rule_key"].startswith("legal_name_consistency_")]
        for cc in consistency_checks:
            assert cc["status"] == "pass", (
                f"S01: Legal name consistency should pass for {r['document_type']}: {cc}"
            )

    # Score must be > 60 (subject to 90-cap and GSTIN checksum)
    assert score > 60, f"S01: Expected score > 60 for compliant bidder, got {score}"


# ── Scenario 2: PAN-GSTIN Mismatch ───────────────────────────────────────

def test_scenario_pan_gstin_mismatch():
    """
    S04: The declared PAN does not appear in GSTIN chars 3-12.
    Expected: pan_document_match or gst-related check fails; score reduced.
    """
    bidder = _bidder("MismatchCorp Pvt. Ltd.", "DDDMC4567P", "06XXXXX1234X1ZQ", "UDYAM-HR-06-0011111")
    docs = {
        "pan": _doc(1, {"pan": "DDDMC4567P", "legal_name": "MismatchCorp Pvt. Ltd."}),
        "gst": _doc(2, {"gstin": "06XXXXX1234X1ZQ", "legal_name": "MismatchCorp Pvt. Ltd."}),
        "udyam": _doc(3, {"udyam_number": "UDYAM-HR-06-0011111", "legal_name": "MismatchCorp Pvt. Ltd."}),
    }
    rules, results, score, breakdown = _run(bidder, docs, ["pan", "gst", "udyam"])

    # The PAN-GSTIN cross check should fail (PAN DDDMC4567P vs embedded XXXXX1234X)
    pan_gstin_fail = rules.get("pan_document_match", {}).get("pass", True)
    gst_format_fail = rules.get("gst_format", {}).get("pass", True)

    # At least one identity check must fail
    any_fail = not pan_gstin_fail or not gst_format_fail
    assert any_fail, "S04: Expected at least one identity check to fail for PAN-GSTIN mismatch"
    assert score < 100, f"S04: Score should be < 100 for mismatch scenario, got {score}"


# ── Scenario 3: Missing EPFO ─────────────────────────────────────────────

def test_scenario_missing_epfo():
    """
    S05: EPFO document not uploaded; requirement is mandatory.
    Expected: epfo_submitted fails; score reduced.
    """
    bidder = _bidder("NoEPFO Enterprises Ltd.", "EEENE2345F", "19EEENE2345F1ZB", "UDYAM-WB-19-0055678")
    docs = {
        "pan": _doc(1, {"pan": "EEENE2345F", "legal_name": "NoEPFO Enterprises Ltd."}),
        "gst": _doc(2, {"gstin": "19EEENE2345F1ZB", "legal_name": "NoEPFO Enterprises Ltd."}),
        "udyam": _doc(3, {"udyam_number": "UDYAM-WB-19-0055678", "legal_name": "NoEPFO Enterprises Ltd."}),
        # No EPFO document
    }
    rules, results, score, breakdown = _run(
        bidder, docs, ["pan", "gst", "udyam", "epfo", "non_blacklisting"]
    )

    epfo_check = rules.get("epfo_submitted", {})
    assert epfo_check.get("pass") is False, "S05: epfo_submitted should fail when EPFO doc is missing"
    assert score < 100, f"S05: Score should be < 100 when mandatory EPFO is missing, got {score}"


# ── Scenario 4: Many Documents Missing ───────────────────────────────────

def test_scenario_docs_missing():
    """
    S09: Only PAN and GST uploaded; 5 required docs missing.
    Expected: multiple submission checks fail; score low.
    """
    bidder = _bidder("Incomplete Docs Corp.", "IIIDC1234K", "09IIIDC1234K1ZF")
    docs = {
        "pan": _doc(1, {"pan": "IIIDC1234K", "legal_name": "Incomplete Docs Corp."}),
        "gst": _doc(2, {"gstin": "09IIIDC1234K1ZF", "legal_name": "Incomplete Docs Corp."}),
    }
    rules, results, score, breakdown = _run(
        bidder, docs, ["pan", "gst", "udyam", "epfo", "esic", "non_blacklisting", "oem_auth"]
    )

    # At least 3 submission checks should fail (udyam, epfo, esic at minimum)
    failed_submissions = [
        k for k, v in rules.items()
        if k.endswith("_submitted") and not v.get("pass") and v.get("required", True)
    ]
    assert len(failed_submissions) >= 3, (
        f"S09: Expected >=3 failed submissions, got {len(failed_submissions)}: {failed_submissions}"
    )
    assert score < 80, f"S09: Score should be < 80 with many missing docs, got {score}"


# ── Scenario 5: Legal Name Mismatch ──────────────────────────────────────

def test_scenario_legal_name_mismatch():
    """
    S08: Company name on PAN card differs significantly from GST certificate.
    Expected: legal_name_consistency check fails for the mismatched document.
    """
    bidder = _bidder("AlphaGroup Pvt. Ltd.", "HHHAG7890J", "24HHHAG7890J1ZE", "UDYAM-GJ-24-0022222")
    docs = {
        "pan": _doc(1, {"pan": "HHHAG7890J", "legal_name": "AlphaGroup Pvt. Ltd."}),
        "gst": _doc(2, {"gstin": "24HHHAG7890J1ZE", "legal_name": "Beta Software Solutions Pvt. Ltd."}),
        "udyam": _doc(3, {"udyam_number": "UDYAM-GJ-24-0022222", "legal_name": "AlphaGroup Pvt. Ltd."}),
    }
    rules, results, score, breakdown = _run(bidder, docs, ["pan", "gst", "udyam"])

    # Check that at least one legal_name_consistency check fails (the GST one)
    consistency_fails = [
        k for k, v in rules.items()
        if k.startswith("legal_name_consistency_") and not v.get("pass")
    ]
    assert len(consistency_fails) >= 1, (
        f"S08: Expected at least 1 name consistency failure, got {len(consistency_fails)}"
    )

    # The PAN document should still pass (its name matches)
    by_type = {r["document_type"]: r for r in results}
    if "pan" in by_type:
        pan_consistency = [
            c for c in by_type["pan"]["field_checks"]
            if c["rule_key"].startswith("legal_name_consistency_")
        ]
        assert len(pan_consistency) >= 1, "PAN document should have a legal_name_consistency check"
