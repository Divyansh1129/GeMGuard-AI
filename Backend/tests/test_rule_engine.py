"""
tests/test_rule_engine.py
-------------------------
Proves the four required invariants of the DocumentVerificationResult design:

1. All checks pass => status pass; high score; no contradictory flag.
2. Required field fails despite high extraction confidence => status fail; score reflects fail.
3. Same company name across 10 docs => every document gets pass legal-name consistency field check.
4. One document with a different PAN => only that document gets fail; other docs remain pass.
"""
import sys
import os
import pytest

# Allow imports from Backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.rule_engine import (
    run_rule_checks,
    build_document_results,
    normalise_name,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bidder(**overrides):
    base = {
        "company_name": "Acme Pvt. Ltd.",
        "pan_number": "ABCDE1234F",
        "gstin": "27ABCDE1234F1Z0",
        "udyam_number": "UDYAM-MH-01-0000001",
    }
    base.update(overrides)
    return base


def _make_doc(doc_id, doc_type, fields, confidence=0.98):
    """Build a document dict the way _latest_documents() returns them."""
    merged = {**fields, "confidence": confidence}
    return {
        "id": doc_id,
        "fields": merged,
        "has_text": True,
    }


def _requirements_for(*keys):
    """Create a minimal requirement list with the given keys marked mandatory."""
    return [{"requirement_key": k, "mandatory": True, "source_evidence": ""} for k in keys]


# ---------------------------------------------------------------------------
# Test 1 — All checks pass => overall_status "pass", high score, no fail flag
# ---------------------------------------------------------------------------

def test_all_checks_pass():
    """When every compliance check passes, every document must show
    overall_status='pass', a score of 100, and zero field_checks with
    status='fail'."""
    bidder = _make_bidder()
    documents = {
        "pan": _make_doc(1, "pan", {
            "pan": "ABCDE1234F",
            "legal_name": "Acme Pvt. Ltd.",
        }),
        "gst": _make_doc(2, "gst", {
            "gstin": "27ABCDE1234F1Z0",
            "legal_name": "Acme Pvt. Ltd.",
        }),
        "udyam": _make_doc(3, "udyam", {
            "udyam_number": "UDYAM-MH-01-0000001",
            "legal_name": "Acme Pvt. Ltd.",
        }),
    }
    requirements = _requirements_for("pan", "gst", "udyam")

    rules = run_rule_checks(bidder, documents, requirements)
    results = build_document_results(documents, rules)

    for r in results:
        assert r["overall_status"] == "pass", (
            f"Document {r['document_type']} should be 'pass' but got '{r['overall_status']}'. "
            f"Field checks: {r['field_checks']}"
        )
        assert r["overall_score"] == 100, (
            f"Document {r['document_type']} score should be 100 but got {r['overall_score']}"
        )
        fail_checks = [c for c in r["field_checks"] if c["status"] == "fail"]
        assert len(fail_checks) == 0, (
            f"Document {r['document_type']} has contradictory fail checks: {fail_checks}"
        )

    print("✓ Test 1 PASSED: all checks pass => status pass, score 100, no fail flags")


# ---------------------------------------------------------------------------
# Test 2 — Required field fails despite high extraction confidence => fail
# ---------------------------------------------------------------------------

def test_required_field_fails_with_high_confidence():
    """A document can have 98% extraction confidence yet still fail
    compliance if the extracted PAN does not match the declared one.
    overall_status must be 'fail' and score must reflect the failure."""
    bidder = _make_bidder(pan_number="ABCDE1234F")
    documents = {
        "pan": _make_doc(1, "pan", {
            "pan": "ZZZZZ9999Z",  # wrong PAN — does not match declared
            "legal_name": "Acme Pvt. Ltd.",
        }, confidence=0.98),
    }
    requirements = _requirements_for("pan")

    rules = run_rule_checks(bidder, documents, requirements)
    results = build_document_results(documents, rules)

    pan_result = results[0]

    # Extraction confidence is high
    assert pan_result["extraction_confidence"] == 0.98, (
        f"Extraction confidence should be 0.98, got {pan_result['extraction_confidence']}"
    )
    # But compliance must fail
    assert pan_result["overall_status"] == "fail", (
        f"overall_status should be 'fail' but got '{pan_result['overall_status']}'. "
        f"Field checks: {pan_result['field_checks']}"
    )
    # Score must be less than 100
    assert pan_result["overall_score"] < 100, (
        f"Score should be < 100 for a failing document, got {pan_result['overall_score']}"
    )

    print("✓ Test 2 PASSED: required field fails with high extraction confidence => status fail, score < 100")


# ---------------------------------------------------------------------------
# Test 3 — Same legal name across 10 docs => every doc gets pass consistency
# ---------------------------------------------------------------------------

def test_same_legal_name_across_10_docs():
    """When all 10 documents carry the exact same legal_name (modulo suffix
    variations like 'Pvt. Ltd.' vs 'Private Limited'), every document must
    receive a pass legal_name_consistency field check."""
    bidder = _make_bidder()
    doc_types = [
        "pan", "gst", "udyam", "epfo", "esic",
        "non_blacklisting", "startup_india", "oem_auth",
        "pan",   # duplicate types are fine — rule engine uses the dict key
        "gst",
    ]
    # Use 10 unique keys to simulate 10 different documents
    doc_keys = [
        "pan", "gst", "udyam", "epfo", "esic",
        "non_blacklisting", "startup_india", "oem_auth",
        "doc_extra_1", "doc_extra_2",
    ]
    name_variants = [
        "Acme Private Limited",
        "Acme Pvt. Ltd.",
        "ACME PVT LTD",
        "Acme Pvt Ltd",
        "acme private limited",
        "ACME PRIVATE LIMITED",
        "Acme Pvt. Ltd",
        "Acme Private Limited",
        "acme pvt ltd",
        "ACME PVT. LTD.",
    ]
    documents = {}
    for i, key in enumerate(doc_keys):
        documents[key] = _make_doc(i + 1, key, {
            "legal_name": name_variants[i],
        })

    # No mandatory requirements — we're only testing cross-doc legal-name checks
    rules = run_rule_checks(bidder, documents)
    results = build_document_results(documents, rules)

    assert len(results) == 10, f"Expected 10 document results, got {len(results)}"

    for r in results:
        consistency_checks = [
            c for c in r["field_checks"]
            if c["rule_key"].startswith("legal_name_consistency_")
        ]
        assert len(consistency_checks) >= 1, (
            f"Document {r['document_type']} has no legal_name_consistency check"
        )
        for cc in consistency_checks:
            assert cc["status"] == "pass", (
                f"Document {r['document_type']} legal_name_consistency should be 'pass' "
                f"but got '{cc['status']}': {cc['reason']}"
            )

    print("✓ Test 3 PASSED: same legal name across 10 docs => every doc gets pass consistency check")


# ---------------------------------------------------------------------------
# Test 4 — One document has different PAN => only that doc fails, rest pass
# ---------------------------------------------------------------------------

def test_one_doc_different_pan():
    """Given 3 documents for PAN, GST, Udyam where the PAN document's
    extracted PAN differs from the bidder's declared PAN, only the PAN
    document must fail. The GST and Udyam documents must remain pass."""
    bidder = _make_bidder(
        pan_number="ABCDE1234F",
        gstin="27ABCDE1234F1Z0",
        udyam_number="UDYAM-MH-01-0000001",
    )
    documents = {
        "pan": _make_doc(1, "pan", {
            "pan": "ZZZZZ9999Z",  # DIFFERENT PAN
            "legal_name": "Acme Pvt. Ltd.",
        }),
        "gst": _make_doc(2, "gst", {
            "gstin": "27ABCDE1234F1Z0",
            "legal_name": "Acme Pvt. Ltd.",
        }),
        "udyam": _make_doc(3, "udyam", {
            "udyam_number": "UDYAM-MH-01-0000001",
            "legal_name": "Acme Pvt. Ltd.",
        }),
    }
    requirements = _requirements_for("pan", "gst", "udyam")

    rules = run_rule_checks(bidder, documents, requirements)
    results = build_document_results(documents, rules)

    by_type = {r["document_type"]: r for r in results}

    # PAN document must fail
    assert by_type["pan"]["overall_status"] == "fail", (
        f"PAN document should fail but got '{by_type['pan']['overall_status']}'"
    )

    # GST must pass
    assert by_type["gst"]["overall_status"] == "pass", (
        f"GST document should pass but got '{by_type['gst']['overall_status']}'. "
        f"Checks: {by_type['gst']['field_checks']}"
    )

    # Udyam must pass
    assert by_type["udyam"]["overall_status"] == "pass", (
        f"Udyam document should pass but got '{by_type['udyam']['overall_status']}'. "
        f"Checks: {by_type['udyam']['field_checks']}"
    )

    # PAN score must be below 100
    assert by_type["pan"]["overall_score"] < 100, (
        f"PAN score should be < 100, got {by_type['pan']['overall_score']}"
    )

    # GST and Udyam scores must be 100
    assert by_type["gst"]["overall_score"] == 100, (
        f"GST score should be 100, got {by_type['gst']['overall_score']}"
    )
    assert by_type["udyam"]["overall_score"] == 100, (
        f"Udyam score should be 100, got {by_type['udyam']['overall_score']}"
    )

    print("✓ Test 4 PASSED: one doc with different PAN => only that doc fails, rest pass")


if __name__ == "__main__":
    test_all_checks_pass()
    test_required_field_fails_with_high_confidence()
    test_same_legal_name_across_10_docs()
    test_one_doc_different_pan()
    print("\n🎉 All 4 test cases passed!")
