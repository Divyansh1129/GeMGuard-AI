"""
tests/test_audit_chain.py
--------------------------
Tests for the tamper-evident audit trail hash chain (TASK 5).
Verifies:
1. Hash is computed and stored on add_audit_log()
2. verify_audit_chain() returns valid=True for an intact chain
3. Modifying a log entry is detected by verify_audit_chain()
4. backfill_hashes() fills pre-migration entries
5. Each entry's prev_hash links to the prior entry's entry_hash
"""
import sys
import os
import json
import pytest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.services import audit_service


# ── Test DB fixture ───────────────────────────────────────────────────────

@pytest.fixture
def db():
    """In-memory SQLite DB for testing — fully isolated."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)

    # Add hash columns (normally done by _ensure_hash_columns but we do it here for test isolation)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE audit_logs ADD COLUMN entry_hash TEXT"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE audit_logs ADD COLUMN prev_hash TEXT"))
            conn.commit()
        except Exception:
            pass

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a test bidder
    bidder = models.Bidder(
        company_name="Test Corp",
        company_type="MSME",
        pan_number="ABCDE1234F",
        gstin="27ABCDE1234F1Z0",
    )
    session.add(bidder)
    session.commit()

    yield session, bidder.id
    session.close()


# ── Tests ─────────────────────────────────────────────────────────────────

def test_add_audit_log_stores_hash(db):
    """add_audit_log must store a non-null entry_hash."""
    session, bidder_id = db
    log = audit_service.add_audit_log(
        session, bidder_id,
        event_type="test_event",
        actor="system",
        details={"key": "value"},
    )
    session.commit()
    assert log.entry_hash is not None, "entry_hash must not be None"
    assert len(log.entry_hash) == 64, f"SHA-256 hash must be 64 hex chars, got {len(log.entry_hash)}"


def test_first_entry_uses_genesis(db):
    """First audit log entry for a bidder must use prev_hash = GENESIS."""
    session, bidder_id = db
    log = audit_service.add_audit_log(
        session, bidder_id,
        event_type="first_event",
        actor="system",
        details="first",
    )
    session.commit()
    assert log.prev_hash == "GENESIS", f"First entry prev_hash must be 'GENESIS', got '{log.prev_hash}'"


def test_chain_links_entries(db):
    """Second entry's prev_hash must equal first entry's entry_hash."""
    session, bidder_id = db

    log1 = audit_service.add_audit_log(
        session, bidder_id, event_type="event_1", actor="system", details="first"
    )
    session.commit()

    log2 = audit_service.add_audit_log(
        session, bidder_id, event_type="event_2", actor="system", details="second"
    )
    session.commit()

    assert log2.prev_hash == log1.entry_hash, (
        f"log2.prev_hash ({log2.prev_hash}) must equal log1.entry_hash ({log1.entry_hash})"
    )


def test_verify_intact_chain(db):
    """verify_audit_chain() must return valid=True for an unmodified chain."""
    session, bidder_id = db

    # Add 3 entries
    for i in range(3):
        audit_service.add_audit_log(
            session, bidder_id, event_type=f"event_{i}", actor="system", details={"step": i}
        )
        session.commit()

    result = audit_service.verify_audit_chain(session, bidder_id)
    assert result["valid"] is True, f"Chain should be intact but got: {result}"
    assert result["total_entries"] == 3
    assert len(result["tampered_entries"]) == 0


def test_verify_detects_tampered_details(db):
    """Modifying log.details after creation must be detected by verify_audit_chain()."""
    session, bidder_id = db

    log = audit_service.add_audit_log(
        session, bidder_id, event_type="tamper_test", actor="system", details="original"
    )
    session.commit()

    # Tamper with the details
    log.details = "TAMPERED"
    session.commit()

    result = audit_service.verify_audit_chain(session, bidder_id)
    assert result["valid"] is False, "Tampered entry must be detected"
    assert log.id in result["tampered_entries"], "Tampered entry ID must appear in tampered_entries"


def test_verify_empty_chain(db):
    """Empty audit trail => valid=True with 0 entries."""
    session, bidder_id = db
    result = audit_service.verify_audit_chain(session, bidder_id)
    assert result["valid"] is True
    assert result["total_entries"] == 0


def test_backfill_hashes(db):
    """backfill_hashes() must populate entry_hash for pre-migration entries."""
    session, bidder_id = db

    # Insert raw entry WITHOUT hashes (simulate pre-migration)
    raw_log = models.AuditLog(
        bidder_id=bidder_id,
        event_type="old_event",
        actor="system",
        details="old entry",
        timestamp=datetime.utcnow(),
    )
    session.add(raw_log)
    session.commit()

    # Verify it has no hash
    session.refresh(raw_log)
    pre_hash = getattr(raw_log, "entry_hash", None)
    assert pre_hash is None, f"Pre-migration entry should have no hash, got {pre_hash}"

    # Backfill
    count = audit_service.backfill_hashes(session, bidder_id)
    assert count == 1, f"Expected 1 entry backfilled, got {count}"

    session.refresh(raw_log)
    post_hash = getattr(raw_log, "entry_hash", None)
    assert post_hash is not None, "After backfill, entry_hash must not be None"
    assert len(post_hash) == 64, f"Backfilled hash must be 64 chars, got {len(post_hash)}"


def test_hash_is_deterministic(db):
    """
    Given the same inputs, the hash must be identical.
    This ensures verify_audit_chain can re-derive hashes.
    """
    from app.services.audit_service import _compute_hash
    ts = datetime(2026, 9, 19, 12, 0, 0)
    hash1 = _compute_hash("GENESIS", "test_event", "system", "details", ts)
    hash2 = _compute_hash("GENESIS", "test_event", "system", "details", ts)
    assert hash1 == hash2, "Same inputs must produce same hash"
    assert len(hash1) == 64
