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
import re
import mimetypes
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
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

    allowed_types = {"pan", "gst", "udyam", "epfo", "esic", "non_blacklisting", "startup_india", "oem_auth"}
    if doc_type not in allowed_types:
        raise HTTPException(status_code=422, detail="Unsupported document type")
    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=415, detail="Only PDF, PNG, JPG, and JPEG files are supported")
    content = await file.read()
    if not content or len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File must be between 1 byte and 10 MB")
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(file.filename or "document"))
    file_path = os.path.join(settings.UPLOAD_DIR, f"{bidder_id}_{doc_type}_{safe_name}")
    with open(file_path, "wb") as f:
        f.write(content)

    # 2. OCR
    try:
        raw_text = ocr_service.extract_text(file_path)
    except Exception as e:
        raw_text = ""
        extraction_error = str(e)
    else:
        extraction_error = None

    # 3. LLM structured extraction
    extracted_fields = llm_service.extract_fields(doc_type, raw_text)
    if extraction_error:
        extracted_fields["error"] = f"OCR failed: {extraction_error}"
    extracted_fields["file_name"] = safe_name
    extracted_fields["file_size"] = len(content)

    # Keep one current file per document type. A replacement must never leave an
    # earlier upload available to a later "View" request.
    previous_documents = (
        db.query(models.Document)
        .filter(models.Document.bidder_id == bidder_id, models.Document.doc_type == doc_type)
        .all()
    )
    for previous in previous_documents:
        if os.path.isfile(previous.file_path):
            os.remove(previous.file_path)
        db.delete(previous)
    db.flush()

    # 4. Save the current upload to DB
    doc = models.Document(
        bidder_id=bidder_id,
        doc_type=doc_type,
        file_path=file_path,
        extracted_text=raw_text,
        extracted_fields=json.dumps(extracted_fields),
        verification_status="pending" if raw_text.strip() else "invalid",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 5. Audit log
    log = models.AuditLog(
        bidder_id=bidder_id, event_type="document_uploaded", actor="system",
        details=json.dumps({"document_id": doc.id, "doc_type": doc_type, "file_name": safe_name, "ocr_characters": len(raw_text)})
    )
    db.add(log)
    db.commit()

    return doc


@router.get("/{bidder_id}", response_model=list[schemas.DocumentOut])
def list_documents(bidder_id: int, db: Session = Depends(get_db)):
    return (db.query(models.Document).filter(models.Document.bidder_id == bidder_id)
            .order_by(models.Document.uploaded_at.desc()).all())


@router.get("/record/{document_id}", response_model=schemas.DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.patch("/{document_id}/fields", response_model=schemas.DocumentOut)
def update_extracted_field(document_id: int, update: schemas.ExtractedFieldUpdate, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    fields = json.loads(doc.extracted_fields or "{}")
    fields[update.field_name] = update.value
    fields["edited_by_officer"] = True
    doc.extracted_fields = json.dumps(fields)
    db.add(models.AuditLog(bidder_id=doc.bidder_id, event_type="extracted_field_updated", actor="procurement_officer", details=json.dumps({"document_id": doc.id, "field": update.field_name})))
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}/file")
def download_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc or not os.path.isfile(doc.file_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    # Content-Disposition:inline lets the browser PDF viewer render the exact uploaded file.
    media_type = mimetypes.guess_type(doc.file_path)[0] or "application/octet-stream"
    return FileResponse(
        doc.file_path,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{os.path.basename(doc.file_path)}"'},
    )
