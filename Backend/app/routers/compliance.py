"""Evidence-driven compliance checks. Authorised registry integrations are deliberately not simulated."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import rule_engine, llm_service

router = APIRouter(prefix="/compliance", tags=["Compliance"])


def _latest_documents(db: Session, bidder_id: int) -> dict:
    docs = db.query(models.Document).filter(models.Document.bidder_id == bidder_id).order_by(models.Document.uploaded_at.desc()).all()
    result = {}
    for doc in docs:
        if doc.doc_type not in result:
            try:
                fields = json.loads(doc.extracted_fields or "{}")
            except json.JSONDecodeError:
                fields = {}
            result[doc.doc_type] = {"id": doc.id, "fields": fields, "has_text": bool((doc.extracted_text or "").strip())}
    return result


@router.post("/run/{bidder_id}", response_model=schemas.ComplianceResult)
def run_compliance_check(bidder_id: int, db: Session = Depends(get_db)):
    bidder = db.query(models.Bidder).filter(models.Bidder.id == bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    documents = _latest_documents(db, bidder_id)
    tender = db.get(models.Tender, bidder.tender_id) if bidder.tender_id else None
    requirements = ([{"requirement_key": item.requirement_key, "mandatory": bool(item.mandatory), "minimum_value": item.minimum_value, "source_evidence": item.source_evidence} for item in tender.requirements] if tender else [])
    rule_results = rule_engine.run_rule_checks({"company_name": bidder.company_name, "pan_number": bidder.pan_number, "gstin": bidder.gstin, "udyam_number": bidder.udyam_number}, documents, requirements)
    if not tender:
        rule_results["tender_requirements"] = {"pass": False, "detail": "No uploaded tender is linked to this bidder; tender-specific evaluation is pending."}
    compliance_score = rule_engine.rule_based_score(rule_results)
    failed = sum(not item["pass"] for key, item in rule_results.items() if key != "registry_confirmation")
    risk_level = "High" if failed >= 5 else "Medium" if failed else "Low"
    risk_probability = round(min(1.0, failed / max(1, len(rule_results) - 1)), 3)
    recommendation = llm_service.generate_recommendation(bidder.company_name, rule_results, risk_probability, compliance_score, risk_level)

    for doc_type, document in documents.items():
        doc = db.get(models.Document, document["id"])
        related_failures = [value for key, value in rule_results.items() if doc_type in key and not value["pass"]]
        doc.verification_status = "invalid" if not document["has_text"] else ("mismatch" if related_failures else "verified")

    check = models.ComplianceCheck(bidder_id=bidder_id, compliance_score=compliance_score, risk_level=risk_level, rule_engine_result=json.dumps(rule_results), ml_risk_probability=risk_probability, ai_recommendation=recommendation)
    db.add(check)
    db.add(models.AuditLog(bidder_id=bidder_id, event_type="evidence_compliance_check_run", actor="system", details=json.dumps({"score": compliance_score, "risk_level": risk_level, "documents_evaluated": list(documents)})))
    db.commit()
    return schemas.ComplianceResult(bidder_id=bidder_id, compliance_score=compliance_score, risk_level=risk_level, rule_engine_result=rule_results, ml_risk_probability=risk_probability, ai_recommendation=recommendation)


@router.get("/{bidder_id}/latest", response_model=schemas.ComplianceResult)
def get_latest_check(bidder_id: int, db: Session = Depends(get_db)):
    check = db.query(models.ComplianceCheck).filter(models.ComplianceCheck.bidder_id == bidder_id).order_by(models.ComplianceCheck.created_at.desc()).first()
    if not check:
        raise HTTPException(status_code=404, detail="No compliance check found — run one first")
    return schemas.ComplianceResult(bidder_id=bidder_id, compliance_score=check.compliance_score, risk_level=check.risk_level, rule_engine_result=json.loads(check.rule_engine_result), ml_risk_probability=check.ml_risk_probability, ai_recommendation=check.ai_recommendation)


@router.post("/{bidder_id}/decision")
def record_officer_decision(bidder_id: int, decision: schemas.OfficerDecision, db: Session = Depends(get_db)):
    if decision.decision not in {"qualified", "disqualified"}:
        raise HTTPException(status_code=422, detail="Decision must be qualified or disqualified")
    check = db.query(models.ComplianceCheck).filter(models.ComplianceCheck.bidder_id == bidder_id).order_by(models.ComplianceCheck.created_at.desc()).first()
    if not check:
        raise HTTPException(status_code=404, detail="No compliance check found")
    check.officer_decision, check.officer_remarks = decision.decision, decision.remarks
    db.add(models.AuditLog(bidder_id=bidder_id, event_type="officer_decision", actor="procurement_officer", details=json.dumps({"decision": decision.decision, "remarks": decision.remarks})))
    db.commit()
    return {"message": "Officer decision recorded", "bidder_id": bidder_id, "decision": check.officer_decision, "remarks": check.officer_remarks}
