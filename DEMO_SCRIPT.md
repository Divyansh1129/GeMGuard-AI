# GeMGuard AI — SIH 2026 Judge Demo Script

**Project Title:** GeMGuard AI (Smart India Hackathon 2026)  
**Problem Statement:** Automated Verification of Bidder Compliance in GeM Procurement  
**Tagline:** *Rakshak = Protector — AI protects procurement integrity; human officer retains authority.*

---

## 🚀 Quick Setup (1 Minute Before Presentation)

Run this single command in terminal:
```cmd
setup.bat
```
*(Or manually: `python scripts/seed_demo.py` then start backend & frontend)*

- **Backend:** `http://localhost:8000` (FastAPI + Swagger Docs at `/docs`)
- **Frontend:** `http://localhost:5173` (React + Tailwind)

---

## 🎬 Act 1: The Procurement Problem & Platform Entry (2 Mins)

### Step 1.1: Officer Portal Login
1. Open `http://localhost:5173`
2. Point out: **Dual Portal Architecture** — Bidder Self-Service vs. Officer Compliance Portal.
3. Login as **Procurement Officer** (`officer@gem.gov.in` / `officer123` or click **"Quick Officer Demo"**).

### Step 1.2: Dashboard Overview
1. Show the **Executive Summary Panel**:
   - Total Bidders Evaluated
   - Risk Level Breakdown (Low / Medium / High)
   - Pending Officer Qualification Decisions
2. Point out the **Disclaimer Banner**:  
   > ⚠️ *"Decision Support System Only — No official government integration claimed. Final qualification authority remains with the Procurement Officer as per GeM GTC."*

---

## 🎬 Act 2: Evaluation of Bidder #1 (TechNova - Compliant) (3 Mins)

### Step 2.1: Overview & Score Breakdown
1. Select **TechNova Solutions Pvt. Ltd.** (Bidder ID #1).
2. Point out the **Compliance Score: 90 / 100** (or weighted score):
   - Explain why it is capped at **90/100**: Direct EPFO/ESIC Government Registry API is not configured ( grounded in extracted OCR evidence + live GST portal search).
   - Show score vs OCR confidence separation (statutory score is NOT confidence %).
3. Show **ML Risk Classifier**: Low Risk (Predicted Probability: 0.05).

### Step 2.2: Evidence & Cross-Document Consistency
1. Click tab **"Document Verification Findings"**:
   - Expand **PAN Card**: Show extracted PAN `AABCT1234E`, Legal Name match.
   - Expand **GST Certificate**: Show offline 10-char PAN match (`AABCT1234E` embedded in `27AABCT1234E1ZP`), state code `27` (Maharashtra).
   - Show **Live GST Portal Search**: Hits public endpoint `sheet.gstincheck.co.in`, verifies Active status.
2. Click tab **"Cross-Document Verification"**:
   - Point out **Consensus Engine**: Legal entity name verified across 7 documents without human intervention.

### Step 2.3: Tamper-Evident Audit Trail & PDF Dossier
1. Click tab **"Audit Trail & Integrity"**:
   - Click **"Verify Hash Chain"**: Show SHA-256 hash linking each event to the previous one (cryptographic tamper evidence).
2. Click **"Export Compliance Dossier (PDF)"**:
   - Opens official PDF compliance report generated dynamically with `fpdf2`.
   - Point out ASCII-sanitized formatting, risk badges, and officer signature block.

### Step 2.4: Officer Qualification Decision
1. Scroll to **Officer Decision Box**:
   - AI Suggestion: **Qualify**
   - Click **Qualify** button, enter remarks: *"All 7 statutory documents verified against extracted evidence."*
   - Submit decision. Note that diff (AI suggestion vs officer action) is logged to audit trail.

---

## 🎬 Act 3: Evaluation of Bidder #2 (Fraudtech - Blacklisted) (2 Mins)

### Step 3.1: Debarment Detection
1. Select **Fraudtech Solutions Pvt. Ltd.** (Bidder ID #2) or use Quick Bidder Demo Login.
2. Point out immediate **RED ALERT**:
   - Risk Level: **HIGH RISK**
   - Score: **10 / 100**
3. Expand **CVC / GeM Blacklist Card**:
   - Show exact PAN match (`BBBFR5678X`) against local JSON debarment registry.
   - Debarment Reason: *"Barred by CVC for fraudulent documentation in tender GEM/2025/B/991234."*

### Step 3.2: Disqualification Flow
1. Note AI Recommendation: **DISQUALIFY IMMEDIATELY**.
2. Click **Disqualify** as Procurement Officer. Decision saved to DB audit log with hash chain anchor.

---

## 🎬 Act 4: Tender Comparison & Self-Service Bidder Portal (2 Mins)

### Step 4.1: Side-by-Side Tender Comparison
1. Navigate to **Tenders > GEM/2026/B/4567890 > Compare Bidders**.
2. Show side-by-side comparison matrix across all 3 bidders:
   - TechNova (90/100, Low Risk, Qualified)
   - Fraudtech (10/100, High Risk, Disqualified)
   - MismatchCorp (55/100, High Risk, Pending)
3. Point out **PAN/GSTIN Masking**: Statutory IDs are masked for privacy (`ABCDE****E`).

### Step 4.2: Bidder Self-View (Quick Switch)
1. Logout and click **"Quick Judge Demo Login"** on Bidder Portal.
2. Show bidder perspective: pre-submission document validation feedback so bidders can fix errors before submitting.

---

## 📊 Key Talking Points for Judges Q&A

| Question | Answer |
|----------|--------|
| **Is this integrated with official Government APIs?** | No. We use an unofficial public GST check endpoint and deterministic mock adapters (clearly labelled) for hackathon evaluation. Production requires authorized GSP/NSDL access. |
| **How does AI handle poor OCR quality?** | We separate OCR Confidence % from Statutory Compliance Score. Unreadable scans trigger `needs_review` status instead of failing the bidder unfairly. |
| **Can a corrupted record be altered in the database?** | Our tamper-evident SHA-256 hash chain detects any out-of-band DB mutation when `verify_audit_chain()` is run. |
| **Does the AI make the final qualification call?** | Never. The platform provides decision support. The Procurement Officer explicitly reviews, decides, and signs off. |
