"""Evidence-driven compliance checks with one reconciled result per document."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import rule_engine, llm_service
router = APIRouter(prefix="/compliance", tags=["Compliance"])

def _latest_documents(db, bidder_id):
    result = {}
    for doc in db.query(models.Document).filter(models.Document.bidder_id == bidder_id).order_by(models.Document.uploaded_at.desc()):
        if doc.doc_type not in result:
            try: fields=json.loads(doc.extracted_fields or "{}")
            except json.JSONDecodeError: fields={}
            result[doc.doc_type]={"id":doc.id,"fields":fields,"has_text":bool((doc.extracted_text or "").strip())}
    return result

def _result_or_legacy(doc):
    try: return json.loads(doc.verification_result) if doc.verification_result else None
    except json.JSONDecodeError: return None

@router.post("/run/{bidder_id}", response_model=schemas.ComplianceResult)
def run_compliance_check(bidder_id: int, db: Session = Depends(get_db)):
    bidder=db.get(models.Bidder,bidder_id)
    if not bidder: raise HTTPException(status_code=404,detail="Bidder not found")
    documents=_latest_documents(db,bidder_id)
    tender=db.get(models.Tender,bidder.tender_id) if bidder.tender_id else None
    requirements=[{"requirement_key":x.requirement_key,"mandatory":bool(x.mandatory),"source_evidence":x.source_evidence} for x in tender.requirements] if tender else []
    rules=rule_engine.run_rule_checks({"company_name":bidder.company_name,"pan_number":bidder.pan_number,"gstin":bidder.gstin,"udyam_number":bidder.udyam_number},documents,requirements)
    if not tender: rule_engine._check(rules,"tender_requirements",list(documents),"tender","needs_review","No tender is linked; tender-specific evaluation is pending.","tender",False)
    results=rule_engine.build_document_results(documents,rules)
    by_id={r["document_id"]:r for r in results}
    for document in documents.values():
        doc=db.get(models.Document,document["id"]); result=by_id[doc.id]
        doc.verification_result=json.dumps(result)
        doc.verification_status={"pass":"verified","fail":"mismatch","needs_review":"pending"}[result["overall_status"]]
        db.add(models.AuditLog(bidder_id=bidder_id,event_type="document_verification_derived",actor="system",details=json.dumps({"document_id":doc.id,"field_checks":result["field_checks"],"overall_status":result["overall_status"],"overall_score":result["overall_score"]})))
    score=rule_engine.rule_based_score(results)
    failed=sum(r["overall_status"]=="fail" for r in results); risk="High" if failed>=5 else "Medium" if failed else "Low"; probability=round(failed/max(1,len(results)),3)
    recommendation=llm_service.generate_recommendation(bidder.company_name,rules,probability,score,risk)
    check=models.ComplianceCheck(bidder_id=bidder_id,compliance_score=score,risk_level=risk,rule_engine_result=json.dumps(rules),ml_risk_probability=probability,ai_recommendation=recommendation)
    db.add(check); db.commit()
    return {"bidder_id":bidder_id,"compliance_score":score,"risk_level":risk,"rule_engine_result":rules,"ml_risk_probability":probability,"ai_recommendation":recommendation,"document_results":results}

@router.get("/{bidder_id}/latest", response_model=schemas.ComplianceResult)
def get_latest_check(bidder_id:int,db:Session=Depends(get_db)):
    check=db.query(models.ComplianceCheck).filter(models.ComplianceCheck.bidder_id==bidder_id).order_by(models.ComplianceCheck.created_at.desc()).first()
    if not check: raise HTTPException(status_code=404,detail="No compliance check found — run one first")
    docs=db.query(models.Document).filter(models.Document.bidder_id==bidder_id).all(); results=[]
    for doc in docs:
        result=_result_or_legacy(doc)
        if not result: result={"document_id":doc.id,"document_type":doc.doc_type,"extraction_confidence":None,"extracted_fields":{},"field_checks":[{"field_name":"document","status":"needs_review","reason":"Pre-migration record, recompute required.","compared_against":None,"required":True,"rule_key":"pre_migration"}],"overall_status":"needs_review","overall_score":50}
        results.append(result)
    return {"bidder_id":bidder_id,"compliance_score":check.compliance_score,"risk_level":check.risk_level,"rule_engine_result":json.loads(check.rule_engine_result),"ml_risk_probability":check.ml_risk_probability,"ai_recommendation":check.ai_recommendation,"document_results":results}

@router.post("/{bidder_id}/decision")
def officer_decision(bidder_id: int, decision: schemas.OfficerDecision, db: Session = Depends(get_db)):
    check = db.query(models.ComplianceCheck).filter(
        models.ComplianceCheck.bidder_id == bidder_id
    ).order_by(models.ComplianceCheck.created_at.desc()).first()
    if not check:
        raise HTTPException(status_code=404, detail="No compliance check found — run one first")
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
