"""
schemas.py
----------
Pydantic models = the "shape" of data going IN and OUT of your API.
Different from models.py (which is the DB table shape).
FastAPI uses these to validate incoming requests and auto-generate the
interactive API docs at /docs.
"""

from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class BidderCreate(BaseModel):
    company_name: str
    company_type: str
    pan_number: Optional[str] = None
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None
    tender_id: Optional[str] = None


class BidderOut(BidderCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # lets Pydantic read directly from SQLAlchemy objects


class BidderUpdate(BaseModel):
    company_name: Optional[str] = None
    pan_number: Optional[str] = None
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None
    tender_id: Optional[str] = None


class FieldCheckOut(BaseModel):
    field_name: str
    status: str
    reason: str
    compared_against: Optional[str] = None
    required: bool = True
    rule_key: str

class DocumentVerificationResultOut(BaseModel):
    document_id: int
    document_type: str
    extraction_confidence: Optional[float] = None
    extracted_fields: dict = {}
    field_checks: list[FieldCheckOut] = []
    overall_status: str
    overall_score: int

class DocumentOut(BaseModel):
    id: int
    doc_type: str
    verification_status: str
    extracted_fields: Optional[str]
    extracted_text: Optional[str] = None
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_at: datetime
    verification_result: Optional[DocumentVerificationResultOut] = None

    class Config:
        from_attributes = True


class ComplianceResult(BaseModel):
    bidder_id: int
    compliance_score: float
    risk_level: str
    rule_engine_result: dict
    ml_risk_probability: float
    ai_recommendation: str
    document_results: list[DocumentVerificationResultOut] = []
    govt_checks: Optional[dict] = None
    blacklist_result: Optional[dict] = None


class OfficerDecision(BaseModel):
    decision: str          # "qualified" or "disqualified"
    remarks: Optional[str] = None


class ExtractedFieldUpdate(BaseModel):
    field_name: str
    value: Any


class TenderRequirementOut(BaseModel):
    requirement_key: str
    label: str
    mandatory: bool
    minimum_value: Optional[float] = None
    unit: Optional[str] = None
    verification_type: str
    source_evidence: Optional[str] = None

    class Config:
        from_attributes = True


class TenderOut(BaseModel):
    id: str
    name: str
    department: Optional[str] = None
    status: str
    created_at: datetime
    requirements: list[TenderRequirementOut] = []

    class Config:
        from_attributes = True
