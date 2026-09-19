"""schemas.py - Pydantic schemas for GeMGuard AI API."""
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
        from_attributes = True


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


class RecommendationSchema(BaseModel):
    """Structured AI recommendation output validated by Pydantic."""
    summary: str
    risk_flags: list[str] = []
    suggested_action: str  # qualify | disqualify | request_more_info
    confidence: float = 0.0  # 0.0 to 1.0
    generated_by: str = "llm"  # llm | rule_fallback


class ScoreBreakdown(BaseModel):
    """Weighted score breakdown by compliance category."""
    raw_score: float
    total: float
    categories: dict = {}
    api_cap_applied: bool = False
    api_cap_limit: Optional[float] = None


class AuditVerifyResult(BaseModel):
    """Result of verify_audit_chain()."""
    valid: bool
    total_entries: int
    tampered_entries: list[int] = []
    backfilled_entries: list[int] = []
    detail: str


class ComplianceResult(BaseModel):
    bidder_id: int
    compliance_score: float
    risk_level: str
    rule_engine_result: dict
    ml_risk_probability: float
    ai_recommendation: str
    ai_recommendation_structured: Optional[RecommendationSchema] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    document_results: list[DocumentVerificationResultOut] = []
    govt_checks: Optional[dict] = None
    blacklist_result: Optional[dict] = None


class OfficerDecision(BaseModel):
    decision: str  # qualified or disqualified
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
