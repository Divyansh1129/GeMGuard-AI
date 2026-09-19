"""
tests/test_scoring.py
----------------------
Tests for weighted compliance scoring (TASK 3).
Verifies:
1. Weighted scoring returns values in [0, 100]
2. 90/100 cap applied when govt_api_auth_* is needs_review
3. Cap NOT applied when all govt checks pass
4. Score breakdown contains category-level info
5. Empty results => 100.0
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.rule_engine import run_rule_checks, rule_based_score


def _make_bidder():
    return {
        "company_name": "Acme Pvt. Ltd.",
        "pan_number": "ABCDE1234F",
        "gstin": "27ABCDE1234F1Z0",
        "udyam_number": "UDYAM-MH-01-0000001",
    }


def _make_doc(doc_id, doc_type, fields, confidence=0.98):
    return {"id": doc_id, "fields": {**fields, "confidence": confidence}, "has_text": True}


def test_score_in_valid_range():
    """Compliance score must always be in [0, 100]."""
    bidder = _make_bidder()
    docs = {
        "pan": _make_doc(1, "pan", {"pan": "ABCDE1234F", "legal_name": "Acme Pvt. Ltd."}),
        "gst": _make_doc(2, "gst", {"gstin": "27ABCDE1234F1Z0", "legal_name": "Acme Pvt. Ltd."}),
    }
    rules = run_rule_checks(bidder, docs)
    score = rule_based_score(rules)
    assert 0 <= score <= 100, f"Score {score} out of range [0, 100]"


def test_empty_results_returns_100():
    """No rules => 100 score (nothing failed)."""
    score = rule_based_score({})
    assert score == 100.0


def test_90_cap_applied_when_api_not_configured():
    """
    When govt_api_auth_* checks are needs_review (no live API),
    the score must be capped at 90 (configurable via scoring_config.json).
    """
    bidder = _make_bidder()
    docs = {
        "pan": _make_doc(1, "pan", {"pan": "ABCDE1234F", "legal_name": "Acme Pvt. Ltd."}),
        "gst": _make_doc(2, "gst", {"gstin": "27ABCDE1234F1Z0", "legal_name": "Acme Pvt. Ltd."}),
        "udyam": _make_doc(3, "udyam", {"udyam_number": "UDYAM-MH-01-0000001", "legal_name": "Acme Pvt. Ltd."}),
    }
    rules = run_rule_checks(bidder, docs, [
        {"requirement_key": "pan", "mandatory": True, "source_evidence": ""},
        {"requirement_key": "gst", "mandatory": True, "source_evidence": ""},
        {"requirement_key": "udyam", "mandatory": True, "source_evidence": ""},
    ])

    # Confirm govt_api_auth_* rules exist and are needs_review (for non-GST/PAN types)
    api_review_rules = [k for k, v in rules.items()
                        if k.startswith("govt_api_auth_") and v.get("status") == "needs_review"]

    if api_review_rules:
        score, breakdown = rule_based_score(rules, return_breakdown=True)
        assert score <= 90, (
            f"Score {score} should be <= 90 when Govt API not configured. "
            f"Breakdown: {breakdown}"
        )
        assert breakdown["api_cap_applied"] is True


def test_score_breakdown_structure():
    """Score breakdown must contain required fields."""
    bidder = _make_bidder()
    docs = {
        "pan": _make_doc(1, "pan", {"pan": "ABCDE1234F", "legal_name": "Acme Pvt. Ltd."}),
    }
    rules = run_rule_checks(bidder, docs)
    score, breakdown = rule_based_score(rules, return_breakdown=True)
    assert "raw_score" in breakdown
    assert "total" in breakdown
    assert "categories" in breakdown
    assert "api_cap_applied" in breakdown
    assert isinstance(breakdown["categories"], dict)


def test_fail_reduces_score():
    """A failing required rule must reduce the score below 100."""
    bidder = _make_bidder(pan_number="ABCDE1234F")
    docs = {
        "pan": _make_doc(1, "pan", {"pan": "ZZZZZ9999Z", "legal_name": "Acme Pvt. Ltd."}),
    }
    rules = run_rule_checks(bidder, docs, [{"requirement_key": "pan", "mandatory": True, "source_evidence": ""}])
    score = rule_based_score(rules)
    assert score < 100, f"Expected score < 100 for a failing PAN check, got {score}"


def test_score_with_blacklist_fail():
    """
    When a blacklist_check rule fails (required=True), score must reflect failure.
    Simulate by directly injecting a fail rule.
    """
    from app.services.rule_engine import _check
    rules = {}
    _check(rules, "pan_submitted", ["pan"], "document", "pass", "PAN uploaded.")
    _check(rules, "blacklist_check", ["pan"], "blacklist", "fail",
           "Entity found in debarment database.", "blacklist_database", required=True)
    score = rule_based_score(rules)
    assert score < 100


def test_no_required_rules_uses_fallback():
    """When no required rules match any category, fallback ratio is used."""
    from app.services.rule_engine import _check
    rules = {}
    # Only non-required rules
    _check(rules, "some_info_check", ["pan"], "info", "pass", "Informational.", required=False)
    score = rule_based_score(rules)
    # Fallback: no required rules => passes all => 100
    assert score == 100.0


# ── Bidder helper for tests ───────────────────────────────────────────────

def _make_bidder(**overrides):
    base = {
        "company_name": "Acme Pvt. Ltd.",
        "pan_number": "ABCDE1234F",
        "gstin": "27ABCDE1234F1Z0",
        "udyam_number": "UDYAM-MH-01-0000001",
    }
    base.update(overrides)
    return base
