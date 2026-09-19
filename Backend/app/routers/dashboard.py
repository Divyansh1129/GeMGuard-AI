"""
routers/dashboard.py
-----------------------
Endpoints that exist purely to make the frontend's job easy — pre-aggregated
data for the "Compliance Dashboard" screen, instead of making the frontend
stitch together multiple calls itself.

Endpoints:
  GET /dashboard/summary                    -> counts by risk level, total bidders, pending decisions
  GET /dashboard/tenders/{tender_id}/bidders -> tender-level bidder comparison (masked IDs, scores)
  GET /dashboard/{bidder_id}/audit          -> full audit trail for one bidder
"""

import os
import re
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models
from app import schemas
from app.config import settings
from app.services import ocr_service, llm_service, security_utils

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.post("/tenders/upload", response_model=schemas.TenderOut)
async def upload_tender(
    name: str = Form(...), department: str = Form(""), file: UploadFile = File(...), db: Session = Depends(get_db)
):
    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=415, detail="Tender must be a PDF, PNG, JPG, or JPEG")
    content = await file.read()
    if not content or len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Tender file must be between 1 byte and 10 MB")
    tender_id = f"TENDER-{uuid.uuid4().hex[:10].upper()}"
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(file.filename or "tender"))
    path = os.path.join(settings.UPLOAD_DIR, f"{tender_id}_{safe_name}")
    with open(path, "wb") as output:
        output.write(content)
    try:
        text = ocr_service.extract_text(path)
    except Exception as exc:
        text = ""
        extraction_error = str(exc)
    else:
        extraction_error = None
    tender = models.Tender(id=tender_id, name=name.strip(), department=department.strip() or None, file_path=path, extracted_text=text)
    db.add(tender)
    for item in llm_service.extract_tender_requirements(text):
        tender.requirements.append(models.TenderRequirement(**item))
    db.commit()
    db.refresh(tender)
    return tender


@router.get("/tenders", response_model=list[schemas.TenderOut])
def list_tenders(db: Session = Depends(get_db)):
    return db.query(models.Tender).order_by(models.Tender.created_at.desc()).all()


@router.get("/tenders/{tender_id}", response_model=schemas.TenderOut)
def get_tender(tender_id: str, db: Session = Depends(get_db)):
    tender = db.get(models.Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    total_bidders = db.query(models.Bidder).count()

    risk_counts = (
        db.query(models.ComplianceCheck.risk_level, func.count(models.ComplianceCheck.id))
        .group_by(models.ComplianceCheck.risk_level)
        .all()
    )
    risk_breakdown = {level: count for level, count in risk_counts}

    pending_decisions = (
        db.query(models.ComplianceCheck)
        .filter(models.ComplianceCheck.officer_decision == "pending")
        .count()
    )

    return {
        "total_bidders": total_bidders,
        "risk_breakdown": risk_breakdown,
        "pending_officer_decisions": pending_decisions,
    }


@router.get("/tenders/{tender_id}/bidders")
def compare_tender_bidders(tender_id: str, db: Session = Depends(get_db)):
    """
    Tender-level bidder comparison endpoint (TASK 6).
    Returns all bidders participating in a tender with their masked IDs,
    compliance scores, risk levels, and officer decisions for side-by-side review.
    """
    tender = db.get(models.Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    bidders = db.query(models.Bidder).filter(models.Bidder.tender_id == tender_id).all()
    comparison = []

    for b in bidders:
        check = (
            db.query(models.ComplianceCheck)
            .filter(models.ComplianceCheck.bidder_id == b.id)
            .order_by(models.ComplianceCheck.created_at.desc())
            .first()
        )
        doc_count = db.query(models.Document).filter(models.Document.bidder_id == b.id).count()

        comparison.append({
            "bidder_id": b.id,
            "company_name": b.company_name,
            "company_type": b.company_type,
            "pan_masked": security_utils.mask_pan(b.pan_number or ""),
            "gstin_masked": security_utils.mask_gstin(b.gstin or ""),
            "udyam_number": b.udyam_number or "",
            "compliance_score": check.compliance_score if check else None,
            "risk_level": check.risk_level if check else "Pending Run",
            "ml_risk_probability": check.ml_risk_probability if check else None,
            "officer_decision": check.officer_decision if check else "pending",
            "documents_uploaded_count": doc_count,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        })

    return {
        "tender_id": tender_id,
        "tender_name": tender.name,
        "department": tender.department,
        "total_bidders": len(bidders),
        "bidders": comparison,
    }


@router.get("/{bidder_id}/audit")
def bidder_audit_trail(bidder_id: int, db: Session = Depends(get_db)):
    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.bidder_id == bidder_id)
        .order_by(models.AuditLog.timestamp.asc())
        .all()
    )
    return [
        {"event_type": l.event_type, "actor": l.actor, "details": l.details, "timestamp": l.timestamp}
        for l in logs
    ]
