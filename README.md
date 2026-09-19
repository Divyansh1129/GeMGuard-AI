# GeMGuard AI — Smart India Hackathon (SIH) 2026

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Tests-40%20Passed-success.svg)]()

> **Problem Statement:** Automated Verification of Bidder Compliance in GeM Procurement  
> **Tagline:** *Rakshak = Protector — AI protects procurement integrity; human officer retains authority.*

---

## ⚠️ Important Disclaimer & Integration Boundary

> [!IMPORTANT]
> **No official government API integration is claimed or implied.**
> All government registry verification adapters (EPFO, ESIC, MCA21, NSIC, Startup India, DigiLocker, BIS) run in **mock mode** using deterministic sample responses clearly labelled `[SOURCE: mock_*]`. The live GST check queries an **unofficial public endpoint** (`sheet.gstincheck.co.in`), NOT the authenticated GSTN API.
> 
> GeMGuard AI is designed as a **Decision Support System**. Final legal authority for bidder qualification or disqualification rests strictly with the designated Procurement Officer as per GeM General Terms & Conditions.

---

## 🌟 Core Features

- **Document Verification Pipeline:** Tesseract OCR + Groq Llama 3.3 70B field extraction for 8 statutory document types (PAN, GSTIN, Udyam, EPFO, ESIC, Non-Blacklisting, OEM Auth, Startup India).
- **Portal Adapter Layer (11 Adapters):** Abstract adapter pattern with mock/live mode toggle (`ADAPTER_MODE`), 5-minute TTL caching, and exponential back-off retries.
- **28-Feature Random Forest Risk Model:** ML classifier (`risk_model.pkl`) predicting high-risk probability with graceful rule-engine fallback.
- **Weighted Compliance Scoring:** Config-driven (`scoring_config.json`) weighted scoring with a **90/100 cap** when direct government registry APIs are unauthenticated.
- **CVC / GeM Debarment Lookup:** Fuzzy legal name normalization and exact PAN/GSTIN matching against debarment databases.
- **Tamper-Evident Audit Trail:** Cryptographic SHA-256 hash chain linking every audit log entry to the previous entry, with automated chain verification (`GET /compliance/{id}/audit/verify`).
- **Structured AI Recommendation:** Schema-validated (`RecommendationSchema`) AI assessment for procurement officers, with diff-from-AI tracking.
- **Tender-Level Bidder Comparison:** Side-by-side comparison view matrix across bidders participating in the same tender (`GET /dashboard/tenders/{id}/bidders`).
- **PDF Compliance Dossier Export:** Dynamic, ASCII-sanitized report generation via `fpdf2`.
- **Security & Privacy:** Automatic PAN/GSTIN masking (`ABCDE****E`), magic-byte file header validation, and SQLite-to-PostgreSQL ORM swap path.

---

## 🏗️ Architecture & Data Flow

```
   [ Uploaded Document ] ──► [ Tesseract OCR / PyMuPDF ]
                                      │
                                      ▼
                           [ Groq Llama 3.3 70B ]
                        (Structured Field Extraction)
                                      │
                                      ▼
                        ┌─────────────┴─────────────┐
                        │  Rule Engine & Adapters   │
                        └─────────────┬─────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           ▼                          ▼                          ▼
 [ 11 Portal Adapters ]   [ CVC Blacklist Lookup ]   [ 28-Feature RF Model ]
(GST, PAN, Udyam, EPFO...)    (Exact & Fuzzy Match)     (High Risk Predictor)
           │                          │                          │
           └──────────────────────────┼──────────────────────────┘
                                      │
                                      ▼
                        [ Weighted Score Engine ]
                    (90/100 Cap if API Unconfigured)
                                      │
                                      ▼
                     [ Structured AI Recommendation ]
                     (Decision Support for Officer)
                                      │
                                      ▼
                     [ Tamper-Evident Audit Chain ]
                        (SHA-256 Event Hashing)
```

---

## 🛠️ Quick Start (One Command)

### Prerequisites
- Python 3.11+
- Node.js 18+

### Setup & Run
```cmd
setup.bat
```
*(Installs dependencies, runs 40 automated unit tests, and seeds 3 scenario bidders)*

### Manual Commands
```bash
# Backend (Terminal 1)
cd Backend
pip install -r requirements.txt
python ../scripts/seed_demo.py
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd Frontend
npm install
npm run dev
```

---

## 🧪 Testing

Run the full suite of 40 automated tests:
```bash
python -m pytest Backend/tests/ -v
```

Test coverage:
- `test_rule_engine.py`: 4 core invariant tests
- `test_portal_adapters.py`: 18 adapter tests (PAN-GSTIN cross, state code, checksum, mock labelling)
- `test_scoring.py`: 7 weighted scoring and 90-cap tests
- `test_audit_chain.py`: 8 tamper-evident hash chain integrity tests
- `test_e2e_scenarios.py`: 5 end-to-end scenario tests (Fully Compliant, Mismatch, Missing EPFO, etc.)

---

## 📁 Repository Structure

```
GeMGuard AI/
├── AUDIT.md                        ← Task baseline & repository audit
├── DEMO_SCRIPT.md                  ← Step-by-step judge demonstration guide
├── setup.bat                       ← One-command Windows setup script
├── Backend/
│   ├── app/
│   │   ├── config.py               ← App configuration & ADAPTER_MODE
│   │   ├── database.py             ← SQLAlchemy database engine
│   │   ├── main.py                 ← FastAPI entry point & routers
│   │   ├── models.py               ← DB schema (Bidder, Document, ComplianceCheck, AuditLog)
│   │   ├── schemas.py              ← Pydantic v2 schemas
│   │   ├── ml/                     ← Random Forest risk model & training
│   │   ├── routers/                ← API endpoints (bidders, documents, compliance, dashboard)
│   │   └── services/               ← Business logic (adapters, audit, rule engine, LLM, ML)
│   ├── tests/                      ← 40 automated unit & integration tests
│   └── requirements.txt
├── Frontend/                       ← React 19 + Vite + Tailwind CSS UI
├── scripts/
│   ├── generate_data.py            ← Synthetic data generator (40+ bidders, 11 scenarios)
│   └── seed_demo.py                ← One-click demo DB seeder
└── sample_docs/                    ← Sample PDF document evidence
```

---

## 📜 License
Developed for Smart India Hackathon (SIH) 2026.
