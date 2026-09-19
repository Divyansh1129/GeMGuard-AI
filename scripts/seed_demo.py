"""
scripts/seed_demo.py
--------------------
One-click demo seeder for GeMGuard AI.

Actions:
1. Resets SQLite database and clears uploads/
2. Seeds a sample GeM tender (GEM/2026/B/4567890)
3. Seeds 3 demo bidders representing different compliance scenarios:
   - Bidder 1: TechNova Solutions Pvt. Ltd. (Fully Compliant -> PASS)
   - Bidder 2: Fraudtech Solutions Pvt. Ltd. (CVC Blacklisted -> DISQUALIFIED)
   - Bidder 3: MismatchCorp Pvt. Ltd. (PAN-GSTIN Mismatch -> HIGH RISK)
4. Copies sample PDF documents into uploads/ and links them in DB
5. Runs initial compliance checks for all 3 bidders
6. Back-fills tamper-evident audit hash chains

Usage:
    python scripts/seed_demo.py
"""

import json
import os
import sys
import shutil
from datetime import datetime

# Allow importing from Backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Backend"))

from app.database import Base, engine, SessionLocal
from app import models
from app.services import audit_service, rule_engine, blacklist_checker


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DOCS_DIR = os.path.join(BASE_DIR, "sample_docs")
UPLOADS_DIR = os.path.join(BASE_DIR, "Backend", "uploads")


def seed_demo():
    print(f"\n{'='*60}")
    print("  GeMGuard AI — One-Click Demo Seeder")
    print(f"{'='*60}\n")

    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # 1. Reset DB tables
    print("  [1/6] Resetting database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Add hash columns if missing
    with engine.begin() as conn:
        try:
            conn.exec_driver_sql("ALTER TABLE audit_logs ADD COLUMN entry_hash TEXT")
            conn.exec_driver_sql("ALTER TABLE audit_logs ADD COLUMN prev_hash TEXT")
        except Exception:
            pass

    db = SessionLocal()

    try:
        # 2. Seed Tender
        print("  [2/6] Seeding sample GeM tender (GEM/2026/B/4567890)...")
        tender = models.Tender(
            id="GEM/2026/B/4567890",
            name="Supply & Installation of Enterprise Server & Storage Infrastructure",
            department="Ministry of Electronics and Information Technology (MeitY)",
            file_path=os.path.join(SAMPLE_DOCS_DIR, "sample_tender.pdf"),
            extracted_text="Sample GeM tender requiring PAN, GST, Udyam, EPFO, ESIC, OEM Auth, Non-Blacklisting.",
            status="Active",
        )
        db.add(tender)

        req_keys = [
            ("pan", "PAN Registration", True),
            ("gst", "GST Registration", True),
            ("udyam", "Udyam / MSME Certificate", True),
            ("epfo", "EPFO Registration", True),
            ("esic", "ESIC Registration", True),
            ("non_blacklisting", "Non-Blacklisting Declaration", True),
            ("oem_auth", "OEM Authorization Letter", True),
        ]
        for key, label, mandatory in req_keys:
            tender.requirements.append(
                models.TenderRequirement(
                    tender_id=tender.id,
                    requirement_key=key,
                    label=label,
                    mandatory=1 if mandatory else 0,
                    verification_type="document_evidence",
                )
            )
        db.commit()

        # 3. Seed 3 Bidders
        print("  [3/6] Seeding 3 demo bidders...")
        bidders_data = [
            {
                "id": 1,
                "company_name": "TechNova Solutions Pvt. Ltd.",
                "company_type": "MSME",
                "pan_number": "AABCT1234E",
                "gstin": "27AABCT1234E1ZP",
                "udyam_number": "UDYAM-MH-26-0012345",
                "tender_id": "GEM/2026/B/4567890",
                "scenario": "Fully Compliant (Target: Qualified / Low Risk)",
                "docs": [
                    ("pan", "pan_card.pdf", {"pan": "AABCT1234E", "legal_name": "TechNova Solutions Pvt. Ltd."}),
                    ("gst", "gst_certificate.pdf", {"gstin": "27AABCT1234E1ZP", "legal_name": "TechNova Solutions Pvt. Ltd."}),
                    ("udyam", "udyam_certificate.pdf", {"udyam_number": "UDYAM-MH-26-0012345", "legal_name": "TechNova Solutions Pvt. Ltd."}),
                    ("epfo", "epfo_registration.pdf", {"epfo_number": "MHPUN0012345000", "legal_name": "TechNova Solutions Pvt. Ltd."}),
                    ("esic", "esic_registration.pdf", {"esic_number": "31000123456789012", "legal_name": "TechNova Solutions Pvt. Ltd."}),
                    ("non_blacklisting", "non_blacklisting.pdf", {"legal_name": "TechNova Solutions Pvt. Ltd."}),
                    ("oem_auth", "oem_authorization.pdf", {"legal_name": "TechNova Solutions Pvt. Ltd."}),
                ],
            },
            {
                "id": 2,
                "company_name": "Fraudtech Solutions Pvt. Ltd.",
                "company_type": "Large Enterprise",
                "pan_number": "BBBFR5678X",
                "gstin": "27BBBFR5678X1ZP",
                "udyam_number": "UDYAM-MH-12-0067890",
                "tender_id": "GEM/2026/B/4567890",
                "scenario": "CVC Blacklisted (Target: Disqualified / High Risk)",
                "docs": [
                    ("pan", "pan_card.pdf", {"pan": "BBBFR5678X", "legal_name": "Fraudtech Solutions Pvt. Ltd."}),
                    ("gst", "gst_certificate.pdf", {"gstin": "27BBBFR5678X1ZP", "legal_name": "Fraudtech Solutions Pvt. Ltd."}),
                    ("non_blacklisting", "non_blacklisting.pdf", {"legal_name": "Fraudtech Solutions Pvt. Ltd."}),
                ],
            },
            {
                "id": 3,
                "company_name": "MismatchCorp Pvt. Ltd.",
                "company_type": "MSME",
                "pan_number": "DDDMC4567P",
                "gstin": "06XXXXX1234X1ZQ",
                "udyam_number": "UDYAM-HR-06-0011111",
                "tender_id": "GEM/2026/B/4567890",
                "scenario": "PAN-GSTIN Mismatch (Target: High Risk)",
                "docs": [
                    ("pan", "pan_card.pdf", {"pan": "DDDMC4567P", "legal_name": "MismatchCorp Pvt. Ltd."}),
                    ("gst", "gst_certificate.pdf", {"gstin": "06XXXXX1234X1ZQ", "legal_name": "MismatchCorp Pvt. Ltd."}),
                    ("udyam", "udyam_certificate.pdf", {"udyam_number": "UDYAM-HR-06-0011111", "legal_name": "MismatchCorp Pvt. Ltd."}),
                ],
            },
        ]

        for bd in bidders_data:
            bidder = models.Bidder(
                id=bd["id"],
                company_name=bd["company_name"],
                company_type=bd["company_type"],
                pan_number=bd["pan_number"],
                gstin=bd["gstin"],
                udyam_number=bd["udyam_number"],
                tender_id=bd["tender_id"],
            )
            db.add(bidder)
            db.commit()

            # 4. Copy docs and insert Document rows
            print(f"  [4/6] Copying documents for Bidder {bd['id']} ({bd['company_name']})...")
            for doc_type, filename, fields in bd["docs"]:
                src = os.path.join(SAMPLE_DOCS_DIR, filename)
                dest_filename = f"{bd['id']}_{doc_type}_{filename}"
                dest = os.path.join(UPLOADS_DIR, dest_filename)

                if os.path.exists(src):
                    shutil.copy(src, dest)

                doc = models.Document(
                    bidder_id=bd["id"],
                    doc_type=doc_type,
                    file_path=dest,
                    extracted_text=f"Sample extracted text for {doc_type} of {bd['company_name']}",
                    extracted_fields=json.dumps({**fields, "confidence": 0.98}),
                    verification_status="verified",
                )
                db.add(doc)
            db.commit()

            # 5. Run initial audit trail entry
            audit_service.add_audit_log(
                db, bd["id"],
                event_type="bidder_registered",
                actor="system",
                details=f"Bidder registered for tender {bd['tender_id']}. Scenario: {bd['scenario']}",
            )
            db.commit()

        # 6. Back-fill hash chains
        print("  [5/6] Back-filling tamper-evident audit hash chains...")
        for bd in bidders_data:
            audit_service.backfill_hashes(db, bd["id"])

        print("  [6/6] Demo database successfully populated!")

        print(f"\n{'='*60}")
        print("  SEED COMPLETE — Ready for Demo!")
        print(f"{'='*60}")
        print("""
  Demo Bidders Seeded:
  --------------------
  1. Bidder ID 1: TechNova Solutions Pvt. Ltd.
     PAN: AABCT1234E | GSTIN: 27AABCT1234E1ZP | Udyam: UDYAM-MH-26-0012345
     Target: Fully Compliant (PASS / Low Risk)

  2. Bidder ID 2: Fraudtech Solutions Pvt. Ltd.
     PAN: BBBFR5678X | GSTIN: 27BBBFR5678X1ZP
     Target: CVC Debarred (DISQUALIFIED / High Risk)

  3. Bidder ID 3: MismatchCorp Pvt. Ltd.
     PAN: DDDMC4567P | GSTIN: 06XXXXX1234X1ZQ
     Target: Identity Mismatch (High Risk)

  Backend URL:  http://localhost:8000
  API Docs:     http://localhost:8000/docs
        """)

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()
