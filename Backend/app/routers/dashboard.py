"""
routers/dashboard.py
-----------------------
Endpoints that exist purely to make the frontend's job easy — pre-aggregated
data for the "Compliance Dashboard" screen, instead of making the frontend
stitch together multiple calls itself.

Endpoints:
  GET /dashboard/summary            -> counts by risk level, total bidders, pending decisions
  GET /dashboard/{bidder_id}/audit  -> full audit trail for one bidder
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


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