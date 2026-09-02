Absolutely — here’s a polished, GitHub-ready README for **GemGuard AI**, based on your Gem Rakshak project architecture and compliance workflow.

# 🛡️ GemGuard AI

### AI-Powered Tender Bidder Compliance & Risk Assessment Platform

**GemGuard AI** is an intelligent compliance and risk-assessment platform designed to help government procurement officers evaluate bidders participating in **GeM (Government e-Marketplace)** tenders.

It automates bidder verification, statutory compliance checks, document validation, risk prediction, and AI-powered recommendations — while keeping the final decision under the control of the authorized officer.

---

## 🚨 Problem

Government procurement involves evaluating large numbers of bidders against multiple eligibility and statutory requirements.

Traditional verification processes can be:

* ⏳ Time-consuming
* 📄 Highly document-intensive
* 🔍 Difficult to audit
* ⚠️ Vulnerable to human error
* 🔄 Dependent on checking multiple government portals
* 📊 Difficult to use for consistent risk assessment

Officers need to verify information related to:

* GST
* PAN / ITR
* Udyam registration
* EPFO
* ESIC
* Blacklisting
* Startup / MSME status
* Make-in-India requirements
* Financial and statutory compliance

**GemGuard AI brings these checks together into one intelligent workflow.**

---

# 💡 Our Solution

GemGuard AI creates a centralized bidder compliance pipeline:

```text
                    ┌─────────────────────┐
                    │     Bidder Data     │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌────────────────────────────┐
              │  Government Portal Checks  │
              │ GSTN • PAN • Udyam • EPFO  │
              │ ESIC • Blacklist           │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │   Compliance Rule Engine   │
              │   Explainable Rule Checks  │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │       ML Risk Model        │
              │       Random Forest        │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │     AI Recommendation      │
              │       Groq / Llama         │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │     Officer Dashboard      │
              │ Qualify / Disqualify       │
              └────────────────────────────┘
```

---

# ✨ Key Features

## 1. 🔎 Automated Bidder Verification

GemGuard AI consolidates verification across multiple statutory sources.

The platform evaluates:

* Udyam registration
* GST status and returns
* PAN / ITR information
* EPFO compliance
* ESIC compliance
* Blacklist status
* Startup / MSME eligibility
* Other tender-specific eligibility conditions

---

## 2. ⚖️ Explainable Compliance Engine

Instead of producing only a black-box prediction, GemGuard AI performs explicit statutory and tender-rule checks.

Each requirement can be evaluated as:

```text
✅ PASS
❌ FAIL
⚠️ WARNING
```

This makes the system easier for officers to understand and audit.

---

## 3. 🤖 AI Risk Assessment

A **Random Forest machine-learning model** evaluates bidder-related compliance features and generates a risk assessment.

Example features include:

* Portal validity
* Registration status
* GST return compliance
* PAN / ITR default indicators
* EPFO compliance
* ESIC compliance
* Make-in-India content threshold
* Startup / MSME status
* Previous compliance indicators

The ML layer helps identify potentially high-risk bidders requiring closer scrutiny.

---

## 4. 🧠 LLM-Powered Recommendation

GemGuard AI uses **Groq / Llama** to convert structured compliance results into an understandable recommendation.

Instead of simply displaying raw data, the system can explain:

> Why the bidder passed or failed specific requirements.

The AI recommendation acts as a **decision-support layer**, not as a replacement for the authorized officer.

---

## 5. 📊 Officer Dashboard

The dashboard provides a centralized view of bidder compliance.

Officers can review:

* Bidder information
* Verification results
* Compliance rules
* Risk score
* AI recommendation
* Audit history
* Final decision

---

## 6. 🧾 Audit Trail

Every compliance evaluation can be recorded for traceability.

The system maintains information such as:

```text
Bidder
   ↓
Verification
   ↓
Rule Evaluation
   ↓
Risk Assessment
   ↓
AI Recommendation
   ↓
Officer Decision
```

This creates an auditable decision-making process.

---

# 🏗️ System Architecture

```text
┌─────────────────────────────────────────────┐
│                 Frontend                    │
│        Officer / Procurement Dashboard      │
└──────────────────────┬──────────────────────┘
                       │
                       │ REST API
                       ▼
┌─────────────────────────────────────────────┐
│                 FastAPI                     │
│                                             │
│  ┌────────────┐ ┌────────────┐ ┌─────────┐ │
│  │  Bidders   │ │ Documents  │ │Compliance│ │
│  └────────────┘ └────────────┘ └─────────┘ │
│                                             │
│               Dashboard APIs                │
└──────────────────────┬──────────────────────┘
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
   ┌──────────┐ ┌────────────┐ ┌──────────┐
   │  Portal  │ │ Rule Engine│ │ ML Model │
   │ Services │ │            │ │ Random   │
   │          │ │            │ │ Forest   │
   └──────────┘ └────────────┘ └──────────┘
                                     │
                                     ▼
                              ┌────────────┐
                              │ Groq/Llama │
                              │ AI Layer   │
                              └────────────┘
                                     │
                                     ▼
                              ┌────────────┐
                              │ PostgreSQL │
                              │ / Database │
                              └────────────┘
```

---

# 🧩 Technology Stack

### Backend

* **Python**
* **FastAPI**
* **Uvicorn**
* **SQLAlchemy**
* REST APIs

### Artificial Intelligence

* **Scikit-learn**
* **Random Forest**
* **Groq API**
* **Llama**

### Data & Compliance

* Rule-based compliance engine
* Government portal verification services
* Structured bidder data
* Audit logging

### Frontend

The frontend communicates with the FastAPI backend through REST APIs and provides the procurement officer dashboard.

---

# 📁 Project Structure

```text
Gem-Rakshak/
│
├── Backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── routers/
│   │   │   ├── bidders.py
│   │   │   ├── documents.py
│   │   │   ├── compliance.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── services/
│   │   │   ├── mock_portals.py
│   │   │   ├── rule_engine.py
│   │   │   ├── ml.py
│   │   │   ├── llm.py
│   │   │   └── ocr.py
│   │   │
│   │   └── ml/
│   │
│   ├── uploads/
│   ├── .env.example
│   └── requirements.txt
│
└── README.md
```

---

# 🔄 Compliance Workflow

### Step 1 — Bidder Selection

The officer selects or uploads bidder information.

### Step 2 — Data Verification

GemGuard AI verifies relevant bidder information through connected or simulated government portal services.

```text
Udyam
GSTN
PAN
EPFO
ESIC
Blacklist
```

### Step 3 — Rule Evaluation

The compliance engine evaluates predefined statutory and tender-specific conditions.

### Step 4 — Risk Prediction

The Random Forest model analyzes structured compliance features and produces a risk assessment.

### Step 5 — AI Explanation

Groq/Llama generates a natural-language explanation and recommendation based on the structured results.

### Step 6 — Officer Review

The officer reviews:

```text
Verification Results
        +
Rule Results
        +
Risk Assessment
        +
AI Explanation
```

### Step 7 — Final Decision

The authorized officer makes the final:

```text
QUALIFY
   or
DISQUALIFY
```

decision.

---

# 🧠 Why Combine Rules + ML + LLM?

GemGuard AI deliberately uses **three different intelligence layers**.

| Layer         | Purpose                              |
| ------------- | ------------------------------------ |
| Rule Engine   | Determines explicit compliance       |
| ML Model      | Identifies risk patterns             |
| LLM           | Explains results in natural language |
| Human Officer | Makes final decision                 |

This hybrid approach provides both **automation and explainability**.

```text
             RULES
               │
               ▼
        "Is requirement met?"
               │
               ├──────────────┐
               ▼              ▼
             PASS            FAIL
               │              │
               └──────┬───────┘
                      ▼
                 ML MODEL
                      │
                      ▼
                Risk Level
                      │
                      ▼
                 LLM Layer
                      │
                      ▼
              Human Officer
                      │
                      ▼
              Final Decision
```

---

# 🔐 Explainability & Human-in-the-Loop

GemGuard AI is designed as a **decision-support system**.

The AI does **not** independently make the final procurement decision.

Instead:

```text
AI verifies
     ↓
AI analyzes
     ↓
AI explains
     ↓
Officer reviews
     ↓
Officer decides
```

This helps maintain accountability and allows procurement officials to override or investigate AI recommendations when necessary.

---

# 🧪 Development Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd Gem-Rakshak
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file using the provided example:

```bash
cp .env.example .env
```

Configure the required database and AI/API credentials.

## 5. Start the Backend

```bash
uvicorn app.main:app --reload
```

The API will run locally through Uvicorn.

---

# 🔌 API Modules

The backend is organized around dedicated routers:

```text
/api/bidders
/api/documents
/api/compliance
/api/dashboard
```

These modules provide separation between bidder management, document processing, compliance evaluation, and dashboard functionality.

---

# 📈 Example Risk Assessment

A bidder may receive an evaluation such as:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        BIDDER ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GST Compliance       ✅ PASS
PAN Verification     ✅ PASS
Udyam Registration   ✅ PASS
EPFO Compliance      ⚠️ WARNING
ESIC Compliance      ✅ PASS
Blacklist Check      ✅ PASS
ITR Compliance       ❌ FAIL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Risk Level            : MEDIUM
Compliance Status     : REVIEW
AI Recommendation     : Further Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The officer can then inspect the failed/warning conditions before making the final decision.

---

# 🎯 Benefits

### For Procurement Officers

* Faster bidder verification
* Centralized compliance information
* Reduced manual checking
* Explainable risk assessment
* Better auditability

### For Government Procurement

* More standardized verification
* Early identification of risky bidders
* Consistent rule application
* Improved transparency
* Human-controlled final decisions

---

# 🚀 Future Scope

GemGuard AI can be extended with:

* 🔗 Live government portal/API integrations
* 📄 Advanced document OCR
* 🌐 Multilingual document processing
* 📊 Historical bidder risk analytics
* 🔍 Fraud/anomaly detection
* 🧠 Improved ML models using historical procurement data
* 🔐 Role-based access control
* 📝 Automated compliance reports
* 📈 Tender-level analytics
* 🔔 Real-time compliance alerts

---

# 🏆 Vision

> **Making government procurement smarter, faster, explainable, and more accountable with AI.**

GemGuard AI aims to transform bidder verification from a fragmented manual process into an **intelligent, auditable, human-controlled compliance workflow**.

---

# 👥 Team

**GemGuard AI — AI-Powered Government Procurement Compliance**

Built with ❤️ for **Smart India Hackathon 2026**.

---

## 📜 License

This project is intended for educational, research, and hackathon purposes.

Before production deployment, all government portal integrations, statutory rules, security controls, and compliance requirements should be validated with the relevant authorities.
