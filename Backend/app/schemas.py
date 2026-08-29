"""
schemas.py
----------
Pydantic models = the "shape" of data going IN and OUT of your API.
Different from models.py (which is the DB table shape).
FastAPI uses these to validate incoming requests and auto-generate the
interactive API docs at /docs.
"""

from pydantic import BaseModel
from typing import Optional
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


class DocumentOut(BaseModel):
    id: int
    doc_type: str
    verification_status: str
    extracted_fields: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ComplianceResult(BaseModel):
    bidder_id: int
    compliance_score: float
    risk_level: str
    rule_engine_result: dict
    ml_risk_probability: float
    ai_recommendation: str


class OfficerDecision(BaseModel):
    decision: str          # "qualified" or "disqualified"
    remarks: Optional[str] = None