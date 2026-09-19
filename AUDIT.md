# GeMGuard AI — Full Repository Audit
**Audit Date:** 2026-09-19
**Auditor:** Automated (pre-implementation, TASK 0)
**Purpose:** Establish DONE / PARTIAL / MISSING baseline before TASK 1-9 implementation.

---

## Repo Structure Snapshot

```
GeMGuard AI/
├── Backend/
│   ├── app/
│   │   ├── config.py              <- settings / env vars
│   │   ├── database.py            <- SQLite / SQLAlchemy setup
│   │   ├── main.py                <- FastAPI app, 4 routers included
│   │   ├── models.py              <- ORM: Bidder, Tender, TenderRequirement, Document, ComplianceCheck, AuditLog
│   │   ├── schemas.py             <- Pydantic v2 schemas
│   │   ├── ml/
│   │   │   ├── risk_model.pkl     <- trained Random Forest (3.7 MB)
│   │   │   └── train_model.py     <- training script (28 features)
│   │   ├── routers/
│   │   │   ├── bidders.py
│   │   │   ├── compliance.py      <- async, integrates all services
│   │   │   ├── compliance_report_snippet.py  <- orphan snippet (not imported)
│   │   │   ├── dashboard.py       <- summary + audit trail + tender upload
│   │   │   └── documents.py       <- OCR + LLM field extraction
│   │   └── services/
│   │       ├── blacklist_checker.py
│   │       ├── blacklist_data.json  <- 5 fictitious debarred entities
│   │       ├── govt_verification.py <- GST portal + PAN-GSTIN + Udyam
│   │       ├── llm_service.py       <- Groq Llama-3.3-70B + regex fallback
│   │       ├── ml_service.py        <- loads risk_model.pkl, predict_risk()
│   │       ├── mock_portals.py      <- stub that raises RegistryIntegrationUnavailable
│   │       ├── ocr_service.py       <- Tesseract + pdfplumber
│   │       ├── report_generator.py  <- fpdf2 PDF compliance dossier
│   │       └── rule_engine.py       <- PAN/GST/Udyam checks, legal name, scoring
│   ├── tests/
│   │   └── test_rule_engine.py    <- 4 tests (all pass)
│   └── requirements.txt
├── Frontend/
│   └── src/
│       ├── App.jsx
│       ├── pages/
│       │   ├── BidderVerification.jsx
│       │   ├── Dashboard.jsx, DocumentReview.jsx, Login.jsx ...
│       │   └── bidder/
│       │       ├── BidderDashboard.jsx, BidderDocuments.jsx
│       │       ├── BidderLogin.jsx    <- Quick Demo Login buttons
│       │       ├── BidderProfile.jsx, BidderStatus.jsx
│       ├── components/
│       │   ├── bidder/ (BidderLayout, BidderSidebar)
│       │   └── verification/
│       │       ├── AIAssessment.jsx, AuditTrail.jsx
│       │       ├── ComplianceScore.jsx, CrossDocVerification.jsx
│       │       ├── DocumentChecklist.jsx, IssueCard.jsx, OfficerDecision.jsx
│       └── services/
│           ├── api.js, bidderService.js, bidderStore.js
│           ├── documentService.js, tenderService.js
├── generate_samples.py            <- 8 sample PDFs for TechNova (compliant)
├── generate_blacklisted_samples.py <- 2 PDFs for Fraudtech (blacklisted)
├── reset_database.py              <- clears all 6 DB tables + uploads/
└── README.md
```

---

## TASK 1 - Portal Adapter Layer
> Common interface for 11 govt portals; mock/live switch; caching; retries; cross-verify.

| Item | Status | Notes |
|------|--------|-------|
| Common PortalAdapter interface | MISSING | mock_portals.py is a 16-line stub; no base class |
| GST adapter (live) | PARTIAL | govt_verification.verify_gstin_status() - unofficial endpoint; no retry/caching |
| PAN-GSTIN cross-check adapter | PARTIAL | offline only, not wrapped in adapter interface |
| GSTIN state-code adapter | PARTIAL | offline, not wrapped |
| Udyam adapter | PARTIAL | format only, no portal call |
| EPFO adapter | MISSING | format check only |
| ESIC adapter | MISSING | not implemented |
| MCA21 adapter | MISSING | not implemented |
| NSIC adapter | MISSING | not implemented |
| Startup India adapter | MISSING | not implemented |
| DigiLocker adapter | MISSING | not implemented |
| Make in India / BIS adapter | MISSING | not implemented |
| Mock/live toggle per adapter | MISSING | live call hardcoded |
| In-memory caching (TTL) | MISSING | portal hit on every compliance run |
| Retry with exponential back-off | MISSING | single httpx call, 10s timeout |
| Cross-verify across two sources | MISSING | |

ASSUMPTION: EPFO/ESIC/MCA21/NSIC/Startup India/DigiLocker/BIS will use deterministic mock responses
(labelled source: "mock_[portal]"). Mock/live switch via ADAPTER_MODE=mock|live in .env.

---

## TASK 2 - Synthetic Data
> 40+ bidders, scripts/generate_data.py, 11 scenarios, mock portal JSON.

| Item | Status | Notes |
|------|--------|-------|
| scripts/generate_data.py | MISSING | Directory does not exist |
| 40+ bidder profiles | MISSING | Only 2 entities: TechNova + Fraudtech |
| 11 scenario types | MISSING | |
| Mock portal JSON responses | MISSING | |
| Sample PDFs for all scenarios | PARTIAL | 8 PDFs TechNova, 2 Fraudtech; other scenarios missing |

ASSUMPTION: 11 scenarios: (1) Fully compliant, (2) Blacklisted, (3) GST inactive,
(4) PAN-GSTIN mismatch, (5) Missing EPFO, (6) Missing ESIC, (7) Udyam format invalid,
(8) Legal name mismatch, (9) Documents missing >=4, (10) Startup India unverified,
(11) OEM auth missing.

---

## TASK 3 - Bidder-Level Compliance Score + Risk Level
> Weighted, explainable, config-driven, ML graceful fallback.

| Item | Status | Notes |
|------|--------|-------|
| Rule-based compliance score | DONE | rule_engine.rule_based_score() |
| ML risk prediction (Random Forest) | DONE | ml_service.predict_risk(), 28 features |
| ML called from compliance router | DONE | try/except fallback |
| 28 feature builder _build_ml_features() | DONE | in compliance.py |
| Weighted scoring (configurable weights) | MISSING | simple pass-count ratio |
| Per-check weight config (YAML/JSON) | MISSING | |
| Explainability (score contribution per rule) | PARTIAL | field_checks shows status; no weight/contribution field |
| risk_level + compliance_score saved to DB | DONE | ComplianceCheck columns |
| Max 90/100 cap when Govt API not configured | PARTIAL | UI logic only; not enforced in backend |

ASSUMPTION: scoring_config.json with per-category weights. 90/100 cap enforced
in rule_engine.rule_based_score() when any govt_api_auth_* is needs_review.

---

## TASK 4 - AI Recommendation for Officer
> Structured output, schema validation, rule-based fallback, diff-from-AI logging.

| Item | Status | Notes |
|------|--------|-------|
| LLM recommendation (Groq Llama-3.3) | DONE | llm_service.generate_recommendation() |
| Rule-based fallback | DONE | deterministic string on Groq failure |
| Structured JSON output schema | MISSING | returns plain string |
| Pydantic schema for recommendation | MISSING | |
| Diff logging (officer vs AI recommendation) | MISSING | officer decision saved but no diff computed |
| Recommendation stored in DB | DONE | ComplianceCheck.ai_recommendation |

ASSUMPTION: RecommendationSchema Pydantic model with fields: summary, risk_flags[],
suggested_action, confidence, generated_by. LLM prompted to return JSON; fallback constructs schema.
Diff = {ai_suggested, officer_chose, rationale} logged to AuditLog.

---

## TASK 5 - Tamper-Evident Audit Trail
> Hash chain, verify_audit_chain(), endpoint, re-verify action.

| Item | Status | Notes |
|------|--------|-------|
| AuditLog table | DONE | id, bidder_id, event_type, actor, details, timestamp |
| Audit logs written on events | DONE | document verification, govt check, officer decision |
| Hash column in AuditLog | MISSING | no hash / prev_hash column |
| Hash chain linking entries | MISSING | |
| verify_audit_chain() function | MISSING | |
| GET /compliance/{id}/audit/verify endpoint | MISSING | only GET /dashboard/{id}/audit exists |
| Re-verify action in UI | MISSING | |

ASSUMPTION: Hash = SHA256(prev_hash + event_type + actor + details + timestamp).
First entry uses prev_hash = "GENESIS". Existing rows back-filled on first verify call.

---

## TASK 6 - Dashboard
> Bidder view, tender-level comparison, PDF report with all fields.

| Item | Status | Notes |
|------|--------|-------|
| Officer dashboard summary (/dashboard/summary) | DONE | |
| Per-bidder audit trail (/dashboard/{id}/audit) | DONE | |
| Bidder compliance view (officer portal) | DONE | BidderVerification.jsx |
| Bidder self-view portal | DONE | BidderDashboard, BidderStatus, BidderDocuments |
| Tender-level bidder comparison view | MISSING | no side-by-side comparison |
| PDF report download (officer) | DONE | GET /compliance/{id}/report/pdf |
| PDF includes govt checks + blacklist | DONE | |
| PDF includes all extracted field values | PARTIAL | status+score shown; individual field values not listed |
| Tender-comparison PDF | MISSING | |

---

## TASK 7 - Security & Robustness
> PAN/GSTIN masking, file validation, role separation, DB swap path.

| Item | Status | Notes |
|------|--------|-------|
| PAN masking in logs/UI | MISSING | plain text everywhere |
| GSTIN masking in logs/UI | MISSING | plain text everywhere |
| File type validation (extension) | PARTIAL | extension check in documents.py; no MIME magic-byte check |
| File size limit | DONE | MAX_UPLOAD_BYTES = 10 MB |
| Role separation frontend | PARTIAL | separate layouts; no backend auth |
| JWT/session auth on backend | MISSING | all endpoints open |
| PostgreSQL swap path | DONE | DATABASE_URL env var; ORM is DB-agnostic |
| Secrets in .env | DONE | GROQ_API_KEY, DATABASE_URL |
| CORS restricted | MISSING | allow_origins=["*"] in main.py |

---

## TASK 8 - Tests
> Keep 4 existing, add adapter/scoring/audit/chain/e2e tests.

| Item | Status | Notes |
|------|--------|-------|
| Existing 4 rule-engine tests | DONE | tests/test_rule_engine.py, all pass |
| Adapter tests | MISSING | |
| Bidder-level scoring tests | MISSING | |
| Audit trail / hash chain tests | MISSING | |
| End-to-end tests (5 scenario bidders) | MISSING | |
| pytest.ini or pyproject.toml | MISSING | only .pytest_cache exists |

---

## TASK 9 - Demo Readiness
> One-command setup, DEMO_SCRIPT.md, rewrite README.md.

| Item | Status | Notes |
|------|--------|-------|
| README.md (root) | PARTIAL | exists 16 KB; not SIH-ready |
| DEMO_SCRIPT.md | MISSING | |
| One-command setup (Makefile / setup script) | MISSING | |
| Sample data seeded by default | PARTIAL | generate_samples.py must be run manually |
| reset_database.py | DONE | |
| Quick Demo Login buttons (bidder) | DONE | BidderLogin.jsx |
| Demo data pre-loaded on startup | MISSING | |

---

## Cross-Cutting Bugs Found

| # | Issue | Severity | File |
|---|-------|----------|------|
| 1 | compliance_report_snippet.py not imported anywhere - dead file | Low | Backend/app/routers/compliance_report_snippet.py |
| 2 | rule_based_score() in compliance.py called with results (list) but function expects dict of rule results - wrong value silently | HIGH | compliance.py L213 vs rule_engine.py L199 |
| 3 | mock_portals.py only raises exception, not used anywhere; govt_verification.py does its own HTTP; the two are unconnected | Medium | services/mock_portals.py |
| 4 | fpdf2 NOT in requirements.txt - PDF generation fails on fresh install | HIGH | Backend/requirements.txt |
| 5 | httpx NOT in requirements.txt - async govt checks fail on fresh install | HIGH | Backend/requirements.txt |
| 6 | _build_ml_features() passes results as list to rule_based_score() which calls .values() - type mismatch | HIGH | compliance.py L84 |
| 7 | No scripts/ directory exists (needed for TASK 2) | Low | repo root |
| 8 | AuditLog has no hash/prev_hash columns - DB migration needed for TASK 5 | Medium | models.py |
| 9 | CORS allow_origins=["*"] - should be restricted | Low | main.py |
| 10 | gem_compliance.db committed to git | Medium | .gitignore |

---

## Summary Table

| Task | Area | Status |
|------|------|--------|
| TASK 1 | Portal Adapter Layer | PARTIAL (GST live partial; 8/11 adapters MISSING) |
| TASK 2 | Synthetic Data | MISSING (scripts/generate_data.py does not exist) |
| TASK 3 | Bidder Compliance Score + Risk | PARTIAL (ML + rule score DONE; weights + 90-cap MISSING) |
| TASK 4 | AI Recommendation (structured) | PARTIAL (text DONE; schema + diff-log MISSING) |
| TASK 5 | Tamper-Evident Audit Trail | PARTIAL (logs DONE; hash chain MISSING) |
| TASK 6 | Dashboard | PARTIAL (per-bidder DONE; tender comparison MISSING) |
| TASK 7 | Security & Robustness | PARTIAL (file limits DONE; masking + auth MISSING) |
| TASK 8 | Tests | PARTIAL (4 rule tests DONE; 5 test files MISSING) |
| TASK 9 | Demo Readiness | PARTIAL (reset + quick-login DONE; DEMO_SCRIPT + 1-cmd MISSING) |

Critical bugs to fix before TASK 1: Issues #2, #4, #5, #6 (requirements.txt + rule_based_score type mismatch).
