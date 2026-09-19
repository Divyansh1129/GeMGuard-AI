"""
audit_service.py
-----------------
Tamper-evident audit trail with SHA-256 hash chain.

Each AuditLog entry is linked to the previous one via:
    entry_hash = SHA256(prev_hash + event_type + actor + details + timestamp_iso)

The first entry in any chain uses prev_hash = "GENESIS".

On-write: hash is computed and stored when the audit log entry is created.
Verify:   verify_audit_chain() re-computes hashes and detects any tampering.

NOTE: This uses application-level hashing (no hardware HSM). It provides
      evidence of in-application tampering but is not cryptographically
      secure against a compromised database administrator.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app import models


# ──────────────────────────────────────────────────────────────────────────
# Migration helpers — columns are added lazily
# ──────────────────────────────────────────────────────────────────────────

def _ensure_hash_columns(db: Session) -> None:
    """Add entry_hash and prev_hash columns to audit_logs if missing (SQLite ALTER TABLE)."""
    try:
        db.execute(
            __import__("sqlalchemy").text(
                "ALTER TABLE audit_logs ADD COLUMN entry_hash TEXT"
            )
        )
        db.commit()
    except Exception:
        db.rollback()

    try:
        db.execute(
            __import__("sqlalchemy").text(
                "ALTER TABLE audit_logs ADD COLUMN prev_hash TEXT"
            )
        )
        db.commit()
    except Exception:
        db.rollback()


# ──────────────────────────────────────────────────────────────────────────
# Core hash logic
# ──────────────────────────────────────────────────────────────────────────

def _compute_hash(prev_hash: str, event_type: str, actor: str,
                  details: str, timestamp: datetime) -> str:
    """Deterministic SHA-256 over all mutable audit fields."""
    ts_iso = timestamp.replace(tzinfo=timezone.utc).isoformat() if timestamp.tzinfo is None \
        else timestamp.isoformat()
    payload = f"{prev_hash}|{event_type}|{actor}|{details or ''}|{ts_iso}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ──────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────

def add_audit_log(
    db: Session,
    bidder_id: int,
    event_type: str,
    actor: str,
    details: dict | str,
    prev_hash: Optional[str] = None,
) -> models.AuditLog:
    """
    Create an AuditLog entry with a hash linking it to the previous entry.

    If prev_hash is None, automatically fetches the last entry for this bidder.
    If no previous entry exists, uses 'GENESIS' as the anchor.

    Returns the newly created (and db.add()-ed but not yet committed) AuditLog.
    """
    _ensure_hash_columns(db)

    details_str = json.dumps(details, default=str) if isinstance(details, dict) else str(details)

    # Fetch prev_hash from last existing entry if not provided
    if prev_hash is None:
        last = (
            db.query(models.AuditLog)
            .filter(models.AuditLog.bidder_id == bidder_id)
            .order_by(models.AuditLog.timestamp.desc())
            .first()
        )
        if last:
            try:
                prev_hash = getattr(last, "entry_hash", None) or "BACKFILLED"
            except AttributeError:
                prev_hash = "BACKFILLED"
        else:
            prev_hash = "GENESIS"

    now = datetime.utcnow()
    entry_hash = _compute_hash(prev_hash, event_type, actor, details_str, now)

    log = models.AuditLog(
        bidder_id=bidder_id,
        event_type=event_type,
        actor=actor,
        details=details_str,
        timestamp=now,
    )
    # Set hash columns dynamically (graceful if column not yet migrated)
    try:
        log.entry_hash = entry_hash
        log.prev_hash = prev_hash
    except AttributeError:
        pass

    db.add(log)
    return log


def verify_audit_chain(db: Session, bidder_id: int) -> dict:
    """
    Verify the integrity of the audit trail for a bidder.

    Re-computes each entry's hash and checks it matches the stored hash,
    and that prev_hash matches the previous entry's hash.

    Returns:
        {
            "valid": bool,
            "total_entries": int,
            "tampered_entries": list[int],   # entry IDs with hash mismatches
            "backfilled_entries": list[int], # entries with no hash (pre-migration)
            "detail": str
        }
    """
    _ensure_hash_columns(db)

    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.bidder_id == bidder_id)
        .order_by(models.AuditLog.timestamp.asc(), models.AuditLog.id.asc())
        .all()
    )

    tampered = []
    backfilled = []
    prev_hash = "GENESIS"

    for log in logs:
        stored_hash = getattr(log, "entry_hash", None)
        stored_prev = getattr(log, "prev_hash", None)

        if not stored_hash:
            # Pre-migration entry — record but don't mark as tampered
            backfilled.append(log.id)
            prev_hash = "BACKFILLED"
            continue

        # Re-compute
        expected = _compute_hash(
            stored_prev or prev_hash,
            log.event_type,
            log.actor,
            log.details or "",
            log.timestamp,
        )

        if expected != stored_hash:
            tampered.append(log.id)

        prev_hash = stored_hash

    valid = len(tampered) == 0
    return {
        "valid": valid,
        "total_entries": len(logs),
        "tampered_entries": tampered,
        "backfilled_entries": backfilled,
        "detail": (
            f"Audit chain verified. {len(logs)} entries checked; "
            f"{len(backfilled)} pre-migration (no hash). Chain integrity: {'INTACT' if valid else 'COMPROMISED'}."
            if valid
            else f"TAMPER DETECTED in {len(tampered)} entries: IDs {tampered}."
        ),
    }


def backfill_hashes(db: Session, bidder_id: int) -> int:
    """
    Back-fill entry_hash and prev_hash for pre-migration AuditLog entries.
    Call once per bidder after migrating the schema.
    Returns number of entries updated.
    """
    _ensure_hash_columns(db)

    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.bidder_id == bidder_id)
        .order_by(models.AuditLog.timestamp.asc(), models.AuditLog.id.asc())
        .all()
    )

    prev_hash = "GENESIS"
    updated = 0

    for log in logs:
        existing = getattr(log, "entry_hash", None)
        if existing:
            prev_hash = existing
            continue

        entry_hash = _compute_hash(prev_hash, log.event_type, log.actor,
                                   log.details or "", log.timestamp)
        try:
            log.entry_hash = entry_hash
            log.prev_hash = prev_hash
        except AttributeError:
            break

        prev_hash = entry_hash
        updated += 1

    db.commit()
    return updated
