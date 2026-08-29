"""
routers/bidders.py
--------------------
Endpoints for creating and viewing bidder profiles.
This is usually the FIRST thing that happens: officer/system registers a
bidder for a tender before uploading their documents.

Endpoints:
  POST /bidders/           -> create a new bidder record
  GET  /bidders/{id}       -> fetch one bidder
  GET  /bidders/           -> list all bidders (for the dashboard table)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/bidders", tags=["Bidders"])


@router.post("/", response_model=schemas.BidderOut)
def create_bidder(bidder: schemas.BidderCreate, db: Session = Depends(get_db)):
    db_bidder = models.Bidder(**bidder.dict())
    db.add(db_bidder)
    db.commit()
    db.refresh(db_bidder)

    log = models.AuditLog(
        bidder_id=db_bidder.id, event_type="bidder_created",
        actor="system", details=f"Bidder {db_bidder.company_name} registered"
    )
    db.add(log)
    db.commit()

    return db_bidder


@router.get("/{bidder_id}", response_model=schemas.BidderOut)
def get_bidder(bidder_id: int, db: Session = Depends(get_db)):
    bidder = db.query(models.Bidder).filter(models.Bidder.id == bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")
    return bidder


@router.get("/", response_model=list[schemas.BidderOut])
def list_bidders(db: Session = Depends(get_db)):
    return db.query(models.Bidder).all()