"""
routers/compliance.py
------------------------
THE CORE ENDPOINT. This is what "Run Compliance Check" on the frontend calls.
Ties together every piece you've built:

  1. mock_portals.py  -> pull (simulated) Udyam/GSTN/PAN/EPFO/ESIC/blacklist data
  2. rule_engine.py    -> pass/fail each statutory check (explainable)
  3. ml_service.py     -> trained RandomForest predicts risk_level + probability
  4. llm_service.py    -> Groq/Llama generates a natural-language recommendation
  5. Save ComplianceCheck row + AuditLog entry

Endpoints:
  POST /compliance/run/{bidder_id}        -> run full verification, returns result
  GET  /compliance/{bidder_id}/latest     -> fetch most recent check result
  POST /compliance/{bidder_id}/decision   -> officer records final qualify/disqualify
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import mock_portals, rule_engine, ml_service, llm_service

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.post("/run/{bidder_id}", response_model=schemas.ComplianceResult)
def run_compliance_check(bidder_id: int, db: Session = Depends(get_db)):
    bidder = db.query(models.Bidder).filter(models.Bidder.id == bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    # --- Step 1: pull portal data (mocked) ---
    portal_data = {
        "udyam": mock_portals.verify_udyam(bidder.udyam_number),
        "gstn": mock_portals.verify_gstn(bidder.gstin),
        "pan": mock_portals.verify_pan(bidder.pan_number),
        "epfo": mock_portals.verify_epfo_esic(bidder.pan_number, applicable=True),
        "esic": mock_portals.verify_epfo_esic(bidder.pan_number, applicable=True),
        "blacklist": mock_portals.check_blacklist_debarment(bidder.pan_number),
    }

    # --- Step 2: rule engine ---
    bidder_dict = {
        "make_in_india_local_content_pct": 55,   # placeholder — would come from bidder-submitted docs
        "make_in_india_required_threshold": 50,
    }
    rule_results = rule_engine.run_rule_checks(bidder_dict, portal_data)
    rule_score = rule_engine.rule_based_score(rule_results)

    # --- Step 3: ML model prediction ---
    features = {
        "udyam_valid": int(portal_data["udyam"].get("valid", False)),
        "udyam_expired": int(portal_data["udyam"].get("status") == "expired"),
        "gst_registered": 1,
        "gst_status_active": int(portal_data["gstn"].get("status") == "active"),
        "gst_returns_filed_pct": portal_data["gstn"].get("returns_filed_pct_last_12m", 0),
        "pan_valid": int(portal_data["pan"].get("valid", False)),
        "itr_filed_last_year": int(portal_data["pan"].get("itr_filed_last_year", False)),
        "income_tax_defaulter": int(portal_data["pan"].get("defaulter_flag", False)),
        "epfo_applicable": 1,
        "epfo_compliant": int(portal_data["epfo"].get("compliant", True)),
        "esic_applicable": 1,
        "esic_compliant": int(portal_data["esic"].get("compliant", True)),
        "make_in_india_local_content_pct": bidder_dict["make_in_india_local_content_pct"],
        "make_in_india_required_threshold": bidder_dict["make_in_india_required_threshold"],
        "startup_india_claimed": 0, "startup_india_verified": 0,
        "nsic_claimed": 0, "nsic_verified": 0,
        "oem_authorization_required": 0, "oem_authorization_provided": 1,
        "blacklisted_flag": int(portal_data["blacklist"].get("blacklisted", False)),
        "debarment_active": int(portal_data["blacklist"].get("debarred", False)),
        "documents_missing_count": 0,
        "name_mismatch_across_docs": 0,
        "document_authenticity_score": 90,
        "turnover_consistency_ratio": 1.0,
        "years_since_registration": 5,
        "past_disputes_count": 0,
    }
    ml_result = ml_service.predict_risk(features)

    # --- Step 4: blend rule score + ML into final compliance score ---
    compliance_score = round(rule_score * 0.6 + (100 - ml_result["high_risk_probability"] * 100) * 0.4, 1)

    # --- Step 5: LLM recommendation ---
    recommendation = llm_service.generate_recommendation(
        bidder.company_name, rule_results, ml_result["high_risk_probability"],
        compliance_score, ml_result["risk_level"]
    )

    # --- Save result ---
    check = models.ComplianceCheck(
        bidder_id=bidder_id,
        compliance_score=compliance_score,
        risk_level=ml_result["risk_level"],
        rule_engine_result=json.dumps(rule_results),
        ml_risk_probability=ml_result["high_risk_probability"],
        ai_recommendation=recommendation,
    )
    db.add(check)
    db.add(models.AuditLog(
        bidder_id=bidder_id, event_type="ai_compliance_check_run", actor="AI",
        details=f"Score: {compliance_score}, Risk: {ml_result['risk_level']}"
    ))
    db.commit()

    return schemas.ComplianceResult(
        bidder_id=bidder_id,
        compliance_score=compliance_score,
        risk_level=ml_result["risk_level"],
        rule_engine_result=rule_results,
        ml_risk_probability=ml_result["high_risk_probability"],
        ai_recommendation=recommendation,
    )


@router.get("/{bidder_id}/latest", response_model=schemas.ComplianceResult)
def get_latest_check(bidder_id: int, db: Session = Depends(get_db)):
    check = (db.query(models.ComplianceCheck)
             .filter(models.ComplianceCheck.bidder_id == bidder_id)
             .order_by(models.ComplianceCheck.created_at.desc())
             .first())
    if not check:
        raise HTTPException(status_code=404, detail="No compliance check found — run one first")
    return schemas.ComplianceResult(
        bidder_id=bidder_id,
        compliance_score=check.compliance_score,
        risk_level=check.risk_level,
        rule_engine_result=json.loads(check.rule_engine_result),
        ml_risk_probability=check.ml_risk_probability,
        ai_recommendation=check.ai_recommendation,
    )



@router.post("/{bidder_id}/decision")
def record_officer_decision(
    bidder_id: int,
    decision: schemas.OfficerDecision,
    db: Session = Depends(get_db)
):
    check = (
        db.query(models.ComplianceCheck)
        .filter(models.ComplianceCheck.bidder_id == bidder_id)
        .order_by(models.ComplianceCheck.created_at.desc())
        .first()
    )

    if not check:
        raise HTTPException(
            status_code=404,
            detail="No compliance check found"
        )

    check.officer_decision = decision.decision
    check.officer_remarks = decision.remarks

    db.add(
        models.AuditLog(
            bidder_id=bidder_id,
            event_type="officer_decision",
            actor="procurement_officer",
            details=f"Decision: {decision.decision}"
        )
    )

    db.commit()
    db.refresh(check)

    return {
        "message": "Officer decision recorded successfully",
        "bidder_id": bidder_id,
        "decision": check.officer_decision,
        "remarks": check.officer_remarks,
    }

