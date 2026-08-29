"""
routers/documents.py
-----------------------
Handles document upload. This is where OCR + LLM extraction actually get
triggered — the "AI Document Verification" capability from the problem statement.

Flow when a document is uploaded:
  1. Save file to disk (./uploads)
  2. ocr_service.extract_text()   -> raw text
  3. llm_service.extract_fields() -> structured JSON (GSTIN, dates, names...)
  4. Save Document row with both raw text + extracted fields
  5. Log to AuditLog

Endpoints:
  POST /documents/upload/{bidder_id}   -> upload one document
  GET  /documents/{bidder_id}          -> list all documents for a bidder
"""

import os
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import ocr_service, llm_service
from app.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload/{bidder_id}", response_model=schemas.DocumentOut)
async def upload_document(
    bidder_id: int,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    bidder = db.query(models.Bidder).filter(models.Bidder.id == bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    # 1. Save file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{bidder_id}_{doc_type}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 2. OCR
    try:
        raw_text = ocr_service.extract_text(file_path)
    except Exception as e:
        raw_text = ""
        print(f"OCR failed: {e}")

    # 3. LLM structured extraction
    extracted_fields = {}
    if raw_text.strip():
        extracted_fields = llm_service.extract_fields(doc_type, raw_text)

    # 4. Save to DB
    doc = models.Document(
        bidder_id=bidder_id,
        doc_type=doc_type,
        file_path=file_path,
        extracted_text=raw_text,
        extracted_fields=json.dumps(extracted_fields),
        verification_status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 5. Audit log
    log = models.AuditLog(
        bidder_id=bidder_id, event_type="document_uploaded", actor="system",
        details=f"{doc_type} document uploaded and processed"
    )
    db.add(log)
    db.commit()

    return doc


@router.get("/{bidder_id}", response_model=list[schemas.DocumentOut])
def list_documents(bidder_id: int, db: Session = Depends(get_db)):
    return db.query(models.Document).filter(models.Document.bidder_id == bidder_id).all()