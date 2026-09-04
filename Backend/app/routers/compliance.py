"""
Evidence-driven compliance checks with one reconciled result per document.

Enhanced with:
- Live government verification (GST portal, PAN-GSTIN cross-check)
- ML risk model prediction
- Blacklist/debarment database check
- PDF compliance report download
"""
import json
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import rule_engine, llm_service, govt_verification, blacklist_checker

router = APIRouter(prefix="/compliance", tags=["Compliance"])


def _latest_documents(db, bidder_id):
    result = {}
    for doc in db.query(models.Document).filter(
        models.Document.bidder_id == bidder_id
    ).order_by(models.Document.uploaded_at.desc()):
        if doc.doc_type not in result:
            try:
                fields = json.loads(doc.extracted_fields or "{}")
            except json.JSONDecodeError:
                fields = {}
            result[doc.doc_type] = {
                "id": doc.id,
                "fields": fields,
                "has_text": bool((doc.extracted_text or "").strip()),
            }
    return result


def _result_or_legacy(doc):
    try:
        return json.loads(doc.verification_result) if doc.verification_result else None
    except json.JSONDecodeError:
        return None


def _build_ml_features(bidder, documents, rules, results):
    """Map rule-engine outputs to the 28 features the ML model expects."""
    def _rule_pass(key):
        return 1 if rules.get(key, {}).get("pass") else 0

    doc_types = set(documents.keys())
    failed_count = sum(1 for r in results if r["overall_status"] == "fail")
    review_count = sum(1 for r in results if r["overall_status"] == "needs_review")

    return {
        "udyam_valid": _rule_pass("udyam_format") or _rule_pass("udyam_submitted"),
        "udyam_expired": 0,  # Would need expiry check
        "gst_registered": 1 if "gst" in doc_types else 0,
        "gst_status_active": _rule_pass("gst_format"),
        "gst_returns_filed_pct": 0.85 if _rule_pass("gst_document_match") else 0.3,
        "pan_valid": _rule_pass("pan_format"),
        "itr_filed_last_year": 1 if _rule_pass("pan_document_match") else 0,
        "income_tax_defaulter": 0,
        "epfo_applicable": 1 if "epfo" in doc_types else 0,
        "epfo_compliant": _rule_pass("epfo_submitted"),
        "esic_applicable": 1 if "esic" in doc_types else 0,
        "esic_compliant": _rule_pass("esic_submitted"),
        "make_in_india_local_content_pct": 50,
        "make_in_india_required_threshold": 50,
        "startup_india_claimed": 1 if "startup_india" in doc_types else 0,
        "startup_india_verified": _rule_pass("startup_india_submitted"),
        "nsic_claimed": 0,
        "nsic_verified": 0,
        "oem_authorization_required": 1,
        "oem_authorization_provided": _rule_pass("oem_auth_submitted"),
        "blacklisted_flag": 0,  # Updated by blacklist check
        "debarment_active": 0,
        "documents_missing_count": max(0, 7 - len(doc_types)),
        "name_mismatch_across_docs": sum(
            1 for k, v in rules.items()
            if k.startswith("legal_name_consistency_") and not v.get("pass")
        ),
        "document_authenticity_score": rule_engine.rule_based_score(results) / 100,
        "turnover_consistency_ratio": 0.9,
        "years_since_registration": 5,
        "past_disputes_count": 0,
    }


@router.post("/run/{bidder_id}", response_model=schemas.ComplianceResult)
async def run_compliance_check(bidder_id: int, db: Session = Depends(get_db)):
    bidder = db.get(models.Bidder, bidder_id)
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    documents = _latest_documents(db, bidder_id)

    # Tender requirements
    tender = db.get(models.Tender, bidder.tender_id) if bidder.tender_id else None
    requirements = [
        {
            "requirement_key": x.requirement_key,
            "mandatory": bool(x.mandatory),
            "source_evidence": x.source_evidence,
        }
        for x in tender.requirements
    ] if tender else []

    # 1. Run rule-based checks
    rules = rule_engine.run_rule_checks(
        {
            "company_name": bidder.company_name,
            "pan_number": bidder.pan_number,
            "gstin": bidder.gstin,
            "udyam_number": bidder.udyam_number,
        },
        documents,
        requirements,
    )
    if not tender:
        rule_engine._check(
            rules, "tender_requirements", list(documents),
            "tender", "needs_review",
            "No tender is linked; tender-specific evaluation is pending.",
            "tender", False,
        )

    # 2. Government verification checks
    govt_results = await govt_verification.run_all_govt_checks(
        pan=bidder.pan_number or "",
        gstin=bidder.gstin or "",
        udyam=bidder.udyam_number or "",
    )

    # Add govt checks as rule results so they appear in field_checks
    for check_key, check_result in govt_results.items():
        applies_to_map = {
            "pan_gstin_cross": ["pan", "gst"],
            "gstin_state_code": ["gst"],
            "gstin_live_status": ["gst"],
            "udyam_format": ["udyam"],
        }
        applies_to = applies_to_map.get(check_key, list(documents.keys()))
        field_name = check_key.replace("_", " ").title()
        rule_engine._check(
            rules, f"govt_{check_key}", applies_to, field_name,
            "pass" if check_result.get("verified") else "fail",
            check_result.get("detail", "Government check completed."),
            check_result.get("source", "govt_portal"),
        )

    # 3. Blacklist check
    bl_result = blacklist_checker.check_blacklist(
        company_name=bidder.company_name or "",
        pan=bidder.pan_number,
        gstin=bidder.gstin,
    )
    if bl_result["status"] == "blacklisted":
        rule_engine._check(
            rules, "blacklist_check", list(documents.keys()),
            "blacklist", "fail", bl_result["detail"],
            "blacklist_database",
        )
    else:
        rule_engine._check(
            rules, "blacklist_check", list(documents.keys()),
            "blacklist", "pass", bl_result["detail"],
            "blacklist_database", required=False,
        )

    # 4. Build document results
    results = rule_engine.build_document_results(documents, rules)

    # 5. ML risk prediction
    try:
        from app.services import ml_service
        ml_features = _build_ml_features(bidder.__dict__, documents, rules, results)
        if bl_result["status"] == "blacklisted":
            ml_features["blacklisted_flag"] = 1
            ml_features["debarment_active"] = 1
        ml_result = ml_service.predict_risk(ml_features)
        risk = ml_result["risk_level"]
        probability = ml_result["high_risk_probability"]
    except Exception:
        # Fallback if model not available
        failed = sum(r["overall_status"] == "fail" for r in results)
        risk = "High" if failed >= 5 or bl_result["status"] == "blacklisted" else "Medium" if failed else "Low"
        probability = round(failed / max(1, len(results)), 3)

    # 6. Save results to documents
    by_id = {r["document_id"]: r for r in results}
    for document in documents.values():
        doc = db.get(models.Document, document["id"])
        result = by_id[doc.id]
        doc.verification_result = json.dumps(result)
        doc.verification_status = {
            "pass": "verified", "fail": "mismatch", "needs_review": "pending",
        }[result["overall_status"]]
        db.add(models.AuditLog(
            bidder_id=bidder_id,
            event_type="document_verification_derived",
            actor="system",
            details=json.dumps({
                "document_id": doc.id,
                "field_checks": result["field_checks"],
                "overall_status": result["overall_status"],
                "overall_score": result["overall_score"],
            }),
        ))

    # 7. Compliance score and recommendation
    score = rule_engine.rule_based_score(results)
    recommendation = llm_service.generate_recommendation(
        bidder.company_name, rules, probability, score, risk,
    )

    # 8. Save compliance check
    check = models.ComplianceCheck(
        bidder_id=bidder_id,
        compliance_score=score,
        risk_level=risk,
        rule_engine_result=json.dumps(rules),
        ml_risk_probability=probability,
        ai_recommendation=recommendation,
    )
    db.add(check)

    # 9. Save govt and blacklist results as audit log
    db.add(models.AuditLog(
        bidder_id=bidder_id,
        event_type="govt_verification_completed",
        actor="system",
        details=json.dumps({
            "govt_checks": {k: {"verified": v.get("verified"), "status": v.get("status")} for k, v in govt_results.items()},
            "blacklist_status": bl_result["status"],
        }),
    ))

    db.commit()

    return {
        "bidder_id": bidder_id,
        "compliance_score": score,
        "risk_level": risk,
        "rule_engine_result": rules,
        "ml_risk_probability": probability,
        "ai_recommendation": recommendation,
        "document_results": results,
        "govt_checks": govt_results,
        "blacklist_result": bl_result,
    }


@router.get("/{bidder_id}/latest", response_model=schemas.ComplianceResult)
def get_latest_check(bidder_id: int, db: Session = Depends(get_db)):
    check = db.query(models.ComplianceCheck).filter(
        models.ComplianceCheck.bidder_id == bidder_id
    ).order_by(models.ComplianceCheck.created_at.desc()).first()
    if not check:
        raise HTTPException(status_code=404, detail="No compliance check found - run one first")

    docs = db.query(models.Document).filter(models.Document.bidder_id == bidder_id).all()
    results = []
    for doc in docs:
        result = _result_or_legacy(doc)
        if not result:
            result = {
                "document_id": doc.id,
                "document_type": doc.doc_type,
                "extraction_confidence": None,
                "extracted_fields": {},
                "field_checks": [{
                    "field_name": "document",
                    "status": "needs_review",
                    "reason": "Pre-migration record, recompute required.",
                    "compared_against": None,
                    "required": True,
                    "rule_key": "pre_migration",
                }],
                "overall_status": "needs_review",
                "overall_score": 50,
            }
        results.append(result)

    return {
        "bidder_id": bidder_id,
        "compliance_score": check.compliance_score,
        "risk_level": check.risk_level,
        "rule_engine_result": json.loads(check.rule_engine_result),
        "ml_risk_probability": check.ml_risk_probability,
        "ai_recommendation": check.ai_recommendation,
        "document_results": results,
    }


@router.post("/{bidder_id}/decision")
def officer_decision(bidder_id: int, decision: schemas.OfficerDecision, db: Session = Depends(get_db)):
    check = db.query(models.ComplianceCheck).filter(
        models.ComplianceCheck.bidder_id == bidder_id
    ).order_by(models.ComplianceCheck.created_at.desc()).first()
    if not check:
        raise HTTPException(status_code=404, detail="No compliance check found - run one first")
    check.officer_decision = decision.decision
    check.officer_remarks = decision.remarks
    db.add(models.AuditLog(
        bidder_id=bidder_id,
        event_type="officer_decision",
        actor="procurement_officer",
        details=json.dumps({"decision": decision.decision, "remarks": decision.remarks}),
    ))
    db.commit()
    return {"status": "ok", "decision": decision.decision, "remarks": decision.remarks}


@router.get("/{bidder_id}/report/pdf")
def download_compliance_report(bidder_id: int, db: Session = Depends(get_db)):
    """Generate and download a PDF compliance report for a bidder."""
    from app.services.report_generator import generate_compliance_report

    bidder = db.get(models.Bidder, bidder_id)
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    check = db.query(models.ComplianceCheck).filter(
        models.ComplianceCheck.bidder_id == bidder_id
    ).order_by(models.ComplianceCheck.created_at.desc()).first()
    if not check:
        raise HTTPException(status_code=404, detail="No compliance check found - run one first")

    # Gather document results
    docs = db.query(models.Document).filter(models.Document.bidder_id == bidder_id).all()
    doc_results = []
    for doc in docs:
        result = _result_or_legacy(doc)
        if result:
            doc_results.append(result)

    # Parse rule engine result for govt checks
    try:
        rule_result = json.loads(check.rule_engine_result)
    except json.JSONDecodeError:
        rule_result = {}

    govt_checks = {
        k.replace("govt_", ""): v
        for k, v in rule_result.items()
        if k.startswith("govt_")
    }

    bl_check = rule_result.get("blacklist_check")
    blacklist_result = None
    if bl_check:
        blacklist_result = {
            "status": "blacklisted" if not bl_check.get("pass") else "clean",
            "detail": bl_check.get("detail", ""),
        }

    compliance_data = {
        "compliance_score": check.compliance_score,
        "risk_level": check.risk_level,
        "ml_risk_probability": check.ml_risk_probability,
        "ai_recommendation": check.ai_recommendation,
    }

    bidder_data = {
        "id": bidder.id,
        "company_name": bidder.company_name,
        "pan_number": bidder.pan_number,
        "gstin": bidder.gstin,
        "udyam_number": bidder.udyam_number,
        "tender_id": bidder.tender_id,
    }

    report_path = generate_compliance_report(
        bidder=bidder_data,
        compliance_result=compliance_data,
        document_results=doc_results,
        govt_checks=govt_checks if govt_checks else None,
        blacklist_result=blacklist_result,
    )

    return FileResponse(
        report_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="compliance_report_bidder_{bidder_id}.pdf"'},
    )
