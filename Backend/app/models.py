"""
models.py
---------
The database tables (SQLAlchemy ORM). One class = one table.
This is the single source of truth for your schema.

Tables:
  Bidder          -> one row per company bidding on a tender
  Document        -> uploaded files per bidder (PAN card, GST cert, Udyam cert...)
  ComplianceCheck -> the result of running verification on a bidder (score, risk, JSON details)
  AuditLog        -> every verification/decision event, for the "auditable record" requirement
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Bidder(Base):
    __tablename__ = "bidders"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    company_type = Column(String)          # MSME / Startup / Large Enterprise / OEM / NSIC
    pan_number = Column(String)
    gstin = Column(String)
    udyam_number = Column(String)
    tender_id = Column(String)             # which GeM tender they're bidding on
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="bidder")
    checks = relationship("ComplianceCheck", back_populates="bidder")


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String)
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text)
    status = Column(String, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    requirements = relationship("TenderRequirement", back_populates="tender", cascade="all, delete-orphan")


class TenderRequirement(Base):
    __tablename__ = "tender_requirements"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String, ForeignKey("tenders.id"), nullable=False)
    requirement_key = Column(String, nullable=False)
    label = Column(String, nullable=False)
    mandatory = Column(Integer, default=1)
    minimum_value = Column(Float)
    unit = Column(String)
    verification_type = Column(String, default="document_evidence")
    source_evidence = Column(Text)
    tender = relationship("Tender", back_populates="requirements")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    bidder_id = Column(Integer, ForeignKey("bidders.id"))
    doc_type = Column(String)              # udyam / gst / pan / epfo / esic / startup_india / nsic / oem_auth
    file_path = Column(String)
    extracted_text = Column(Text)          # raw OCR output
    extracted_fields = Column(Text)        # JSON string of LLM-extracted fields
    verification_status = Column(String, default="pending")  # pending / verified / mismatch / invalid
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    bidder = relationship("Bidder", back_populates="documents")


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    bidder_id = Column(Integer, ForeignKey("bidders.id"))
    compliance_score = Column(Float)
    risk_level = Column(String)            # Low / Medium / High
    rule_engine_result = Column(Text)      # JSON: pass/fail per statutory check
    ml_risk_probability = Column(Float)    # model's predicted probability of high risk
    ai_recommendation = Column(Text)       # LLM-generated recommendation text
    officer_decision = Column(String, default="pending")  # pending / qualified / disqualified
    officer_remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    bidder = relationship("Bidder", back_populates="checks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    bidder_id = Column(Integer, ForeignKey("bidders.id"))
    event_type = Column(String)            # e.g. "document_uploaded", "ai_check_run", "officer_override"
    actor = Column(String)                 # "system" / "AI" / officer username
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
