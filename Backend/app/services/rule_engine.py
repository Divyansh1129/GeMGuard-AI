"""
rule_engine.py
----------------
The DETERMINISTIC, EXPLAINABLE part of your compliance check. No AI here on
purpose — a procurement officer needs to see EXACTLY why a bidder failed a
check, and rules give you that for free (an ML model's "why" is much harder
to defend in an audit).

Takes the mock-portal responses (or real ones, later) and applies pass/fail
logic per requirement from the problem statement. Returns a dict the frontend
dashboard can render directly as a checklist, and that also feeds the ML
model as engineered features (see ml_service.py).
"""


def run_rule_checks(bidder: dict, portal_data: dict) -> dict:
    """
    bidder: dict with tender-specific requirements (thresholds etc.)
    portal_data: dict with udyam/gstn/pan/epfo/esic/blacklist results
                 (from mock_portals.py or real APIs later)
    Returns: dict of {check_name: {"pass": bool, "detail": str}}
    """
    results = {}

    udyam = portal_data.get("udyam", {})
    results["udyam_registration"] = {
        "pass": udyam.get("valid", False) and udyam.get("status") == "active",
        "detail": f"Udyam status: {udyam.get('status', 'unknown')}"
    }

    gstn = portal_data.get("gstn", {})
    results["gst_registration"] = {
        "pass": gstn.get("status") == "active",
        "detail": f"GST status: {gstn.get('status', 'unknown')}"
    }
    results["gst_return_filing"] = {
        "pass": gstn.get("returns_filed_pct_last_12m", 0) >= 80,
        "detail": f"Returns filed: {gstn.get('returns_filed_pct_last_12m', 0)}% (required >=80%)"
    }

    pan = portal_data.get("pan", {})
    results["pan_validity"] = {
        "pass": pan.get("valid", False),
        "detail": "PAN valid" if pan.get("valid") else "PAN invalid/not found"
    }
    results["income_tax_compliance"] = {
        "pass": pan.get("itr_filed_last_year", False) and not pan.get("defaulter_flag", True),
        "detail": f"ITR filed: {pan.get('itr_filed_last_year')}, Defaulter: {pan.get('defaulter_flag')}"
    }

    epfo = portal_data.get("epfo", {})
    results["epfo_compliance"] = {
        "pass": epfo.get("compliant", True),
        "detail": "Compliant" if epfo.get("compliant", True) else "Non-compliant"
    }

    esic = portal_data.get("esic", {})
    results["esic_compliance"] = {
        "pass": esic.get("compliant", True),
        "detail": "Compliant" if esic.get("compliant", True) else "Non-compliant"
    }

    local_content = bidder.get("make_in_india_local_content_pct")
    threshold = bidder.get("make_in_india_required_threshold", 50)
    if local_content is not None:
        results["make_in_india"] = {
            "pass": local_content >= threshold,
            "detail": f"Local content: {local_content}% (required >={threshold}%)"
        }

    blacklist = portal_data.get("blacklist", {})
    results["blacklist_debarment"] = {
        "pass": not blacklist.get("blacklisted", False) and not blacklist.get("debarred", False),
        "detail": "Clear" if not blacklist.get("blacklisted") and not blacklist.get("debarred")
                  else "FLAGGED: blacklisted or debarred"
    }

    return results


def rule_based_score(results: dict) -> float:
    """Simple % of checks passed -> 0-100. Used alongside the ML score."""
    if not results:
        return 0.0
    passed = sum(1 for r in results.values() if r["pass"])
    return round((passed / len(results)) * 100, 1)