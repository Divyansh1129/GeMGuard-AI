"""
scripts/generate_data.py
--------------------------
Generates 40+ synthetic bidder profiles covering 11 compliance scenarios
for GeMGuard AI demo and testing.

Usage:
    python scripts/generate_data.py
    python scripts/generate_data.py --seed-db   # also POSTs to running backend

Output:
    scripts/synthetic_data/
        bidders.json            -- 40+ bidder profiles
        mock_portal_responses/  -- per-scenario adapter mock responses
        sample_docs/            -- per-scenario PDF documents

All data is clearly fictitious. No real company data is used.
No official government API calls are made here.
"""

import json
import os
import sys
import argparse
from fpdf import FPDF

# ── Output directories ─────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "synthetic_data")
DOCS_OUT = os.path.join(OUT, "sample_docs")
PORTAL_OUT = os.path.join(OUT, "mock_portal_responses")
os.makedirs(DOCS_OUT, exist_ok=True)
os.makedirs(PORTAL_OUT, exist_ok=True)

# ── 11 scenario definitions ────────────────────────────────────────────────
SCENARIOS = [
    {
        "scenario_id": "S01",
        "name": "Fully Compliant",
        "description": "All 7 statutory docs present; PAN/GSTIN match; Udyam valid; no blacklist.",
        "company": "TechNova Solutions Pvt. Ltd.",
        "pan": "AABCT1234E",
        "gstin": "27AABCT1234E1ZP",
        "udyam": "UDYAM-MH-26-0012345",
        "docs": ["pan", "gst", "udyam", "epfo", "esic", "non_blacklisting", "oem_auth"],
        "anomalies": [],
    },
    {
        "scenario_id": "S02",
        "name": "Blacklisted Entity",
        "description": "Exact PAN match in CVC/GeM blacklist database.",
        "company": "Fraudtech Solutions Pvt. Ltd.",
        "pan": "BBBFR5678X",
        "gstin": "27BBBFR5678X1ZP",
        "udyam": "UDYAM-MH-12-0067890",
        "docs": ["pan", "gst", "udyam", "non_blacklisting"],
        "anomalies": ["blacklisted"],
    },
    {
        "scenario_id": "S03",
        "name": "GST Inactive / Cancelled",
        "description": "GSTIN status is 'Cancelled' on portal; all other docs pass.",
        "company": "InactiveGST Traders Ltd.",
        "pan": "CCCGT9001K",
        "gstin": "29CCCGT9001K1ZA",
        "udyam": "UDYAM-KA-29-0098765",
        "docs": ["pan", "gst", "udyam", "epfo", "non_blacklisting"],
        "anomalies": ["gst_inactive"],
    },
    {
        "scenario_id": "S04",
        "name": "PAN-GSTIN Mismatch",
        "description": "PAN and GSTIN belong to different entities (embedded PAN mismatch).",
        "company": "MismatchCorp Pvt. Ltd.",
        "pan": "DDDMC4567P",
        "gstin": "06XXXXX1234X1ZQ",  # embedded PAN doesn't match
        "udyam": "UDYAM-HR-06-0011111",
        "docs": ["pan", "gst", "udyam", "non_blacklisting"],
        "anomalies": ["pan_gstin_mismatch"],
    },
    {
        "scenario_id": "S05",
        "name": "Missing EPFO",
        "description": "EPFO document not uploaded; all other docs compliant.",
        "company": "NoEPFO Enterprises Ltd.",
        "pan": "EEENE2345F",
        "gstin": "19EEENE2345F1ZB",
        "udyam": "UDYAM-WB-19-0055678",
        "docs": ["pan", "gst", "udyam", "esic", "non_blacklisting", "oem_auth"],
        "anomalies": ["missing_epfo"],
    },
    {
        "scenario_id": "S06",
        "name": "Missing ESIC",
        "description": "ESIC document not uploaded; establishment likely covered.",
        "company": "NoESIC Systems Ltd.",
        "pan": "FFFNS6789G",
        "gstin": "07FFFNS6789G1ZC",
        "udyam": "UDYAM-DL-07-0099999",
        "docs": ["pan", "gst", "udyam", "epfo", "non_blacklisting"],
        "anomalies": ["missing_esic"],
    },
    {
        "scenario_id": "S07",
        "name": "Invalid Udyam Format",
        "description": "Udyam number uses wrong format (missing state code).",
        "company": "BadUdyam Pvt. Ltd.",
        "pan": "GGGBU3456H",
        "gstin": "33GGGBU3456H1ZD",
        "udyam": "UDYAM-XX-99-9999999",  # XX is invalid state code
        "docs": ["pan", "gst", "udyam", "epfo", "non_blacklisting"],
        "anomalies": ["invalid_udyam"],
    },
    {
        "scenario_id": "S08",
        "name": "Legal Name Mismatch",
        "description": "Company name on PAN card differs significantly from GST certificate.",
        "company": "AlphaGroup Pvt. Ltd.",
        "pan": "HHHAG7890J",
        "gstin": "24HHHAG7890J1ZE",
        "udyam": "UDYAM-GJ-24-0022222",
        "docs": ["pan", "gst", "udyam", "non_blacklisting"],
        "anomalies": ["name_mismatch"],
        "alt_name": "Beta Software Solutions Pvt. Ltd.",  # name on GST cert
    },
    {
        "scenario_id": "S09",
        "name": "Many Documents Missing",
        "description": "Only PAN and GST uploaded; 5 required docs missing.",
        "company": "Incomplete Docs Corp.",
        "pan": "IIIDC1234K",
        "gstin": "09IIIDC1234K1ZF",
        "udyam": "",
        "docs": ["pan", "gst"],
        "anomalies": ["docs_missing"],
    },
    {
        "scenario_id": "S10",
        "name": "Startup India Claimed but Unverified",
        "description": "Bidder claims Startup India status but certificate is OCR-unreadable.",
        "company": "StartupClaim Ventures Pvt. Ltd.",
        "pan": "JJJSC5678L",
        "gstin": "27JJJSC5678L1ZG",
        "udyam": "UDYAM-MH-27-0033333",
        "docs": ["pan", "gst", "udyam", "startup_india", "non_blacklisting"],
        "anomalies": ["startup_unverified"],
    },
    {
        "scenario_id": "S11",
        "name": "OEM Authorization Missing",
        "description": "Bidder quotes OEM products but OEM authorization letter not submitted.",
        "company": "NoOEM Tech Solutions Pvt. Ltd.",
        "pan": "KKKNT9012M",
        "gstin": "29KKKNT9012M1ZH",
        "udyam": "UDYAM-KA-29-0044444",
        "docs": ["pan", "gst", "udyam", "epfo", "esic", "non_blacklisting"],
        "anomalies": ["missing_oem"],
    },
]

# ── Generate 40+ bidders by expanding each scenario ───────────────────────
def _make_bidders(scenarios):
    bidders = []
    idx = 1
    for sc in scenarios:
        # Add 3-5 company variants per scenario
        variants = [
            {"suffix": "", "extra_note": ""},
            {"suffix": " (Branch Office)", "extra_note": ""},
            {"suffix": " II", "extra_note": ""},
        ]
        if sc["scenario_id"] in ("S01", "S02", "S03"):
            variants.append({"suffix": " International", "extra_note": ""})

        for i, variant in enumerate(variants):
            pan_suffix = chr(ord("A") + i)
            pan = sc["pan"][:-1] + pan_suffix if len(sc["pan"]) == 10 else sc["pan"]
            bidder = {
                "bidder_id": idx,
                "scenario_id": sc["scenario_id"],
                "scenario_name": sc["name"],
                "company_name": sc["company"] + variant["suffix"],
                "company_type": "MSME" if "UDYAM" in (sc.get("udyam") or "") else "Large Enterprise",
                "pan_number": pan,
                "gstin": sc["gstin"],
                "udyam_number": sc.get("udyam", ""),
                "docs_uploaded": sc["docs"],
                "anomalies": sc["anomalies"],
                "description": sc["description"],
            }
            bidders.append(bidder)
            idx += 1

    return bidders


# ── PDF document generators ───────────────────────────────────────────────

class DocPDF(FPDF):
    def header_block(self, title, subtitle="", color=(26, 35, 126)):
        self.set_fill_color(*color)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        if subtitle:
            self.set_font("Helvetica", "", 9)
            self.cell(0, 5, subtitle, new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_text_color(0, 0, 0)

    def field(self, label, value):
        self.set_font("Helvetica", "", 10)
        self.cell(75, 7, label + ":", new_x="RIGHT")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, str(value or ""), new_x="LMARGIN", new_y="NEXT")

    def section(self, text):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(230, 235, 245)
        self.cell(0, 8, "  " + text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)


def _save_pdf(pdf, scenario_id, doc_type):
    sc_dir = os.path.join(DOCS_OUT, scenario_id)
    os.makedirs(sc_dir, exist_ok=True)
    path = os.path.join(sc_dir, f"{doc_type}.pdf")
    pdf.output(path)
    return path


def _pan_pdf(sc):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("INCOME TAX DEPARTMENT", "Government of India - PAN Card", (26, 35, 126))
    pdf.section("Permanent Account Number")
    pdf.field("PAN", sc["pan"])
    pdf.field("Legal Name", sc["company"])
    pdf.field("Status", "Company")
    pdf.field("Date of Incorporation", "15/03/2018")
    return _save_pdf(pdf, sc["scenario_id"], "pan_card")


def _gst_pdf(sc):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("GOODS AND SERVICES TAX", "Registration Certificate GST REG-06", (0, 77, 64))
    pdf.section("GST Registration Details")
    legal_name = sc.get("alt_name", sc["company"])
    pdf.field("GSTIN", sc["gstin"])
    pdf.field("Legal Name", legal_name)
    pdf.field("PAN", sc["pan"])
    pdf.field("Status", "Cancelled" if "gst_inactive" in sc["anomalies"] else "Active")
    pdf.field("Registration Date", "01/04/2018")
    return _save_pdf(pdf, sc["scenario_id"], "gst_certificate")


def _udyam_pdf(sc):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("UDYAM REGISTRATION", "Ministry of MSME, Government of India", (230, 81, 0))
    pdf.section("Udyam Certificate")
    pdf.field("Udyam Number", sc["udyam"])
    pdf.field("Legal Name", sc["company"])
    pdf.field("PAN", sc["pan"])
    pdf.field("Enterprise Type", "Micro")
    return _save_pdf(pdf, sc["scenario_id"], "udyam_certificate")


def _epfo_pdf(sc):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("EPFO REGISTRATION", "Employees' Provident Fund Organisation", (27, 94, 32))
    pdf.section("Establishment Registration")
    pdf.field("Establishment Code", "MHPUN" + sc["pan"][:5])
    pdf.field("Legal Name", sc["company"])
    pdf.field("PAN", sc["pan"])
    pdf.field("Status", "Active and Compliant")
    return _save_pdf(pdf, sc["scenario_id"], "epfo_registration")


def _esic_pdf(sc):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("ESIC REGISTRATION", "Employees' State Insurance Corporation", (136, 14, 79))
    pdf.section("Employer Registration")
    pdf.field("ESIC Code", "31000" + sc["pan"][:5] + "000")
    pdf.field("Legal Name", sc["company"])
    pdf.field("PAN", sc["pan"])
    pdf.field("Status", "Active")
    return _save_pdf(pdf, sc["scenario_id"], "esic_registration")


def _non_bl_pdf(sc):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("NON-BLACKLISTING DECLARATION", "Self-Declaration Affidavit", (55, 71, 79))
    pdf.section("Declaration")
    pdf.field("Company", sc["company"])
    pdf.field("PAN", sc["pan"])
    pdf.field("GSTIN", sc["gstin"])
    pdf.field("Date", "01/09/2026")
    pdf.body(
        f"I hereby declare that {sc['company']} has not been blacklisted "
        "or debarred by any government authority in India."
    )
    return _save_pdf(pdf, sc["scenario_id"], "non_blacklisting")


def _oem_pdf(sc):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("OEM AUTHORIZATION LETTER", "Original Equipment Manufacturer Certificate", (74, 20, 140))
    pdf.section("Authorization Details")
    pdf.field("Authorized Entity", sc["company"])
    pdf.field("PAN", sc["pan"])
    pdf.field("OEM Name", "GlobalTech Systems Inc.")
    pdf.field("Valid Until", "31/12/2026")
    pdf.body(
        f"{sc['company']} is authorized as a Platinum Partner for GlobalTech products in India."
    )
    return _save_pdf(pdf, sc["scenario_id"], "oem_authorization")


def _startup_pdf(sc, readable=True):
    pdf = DocPDF()
    pdf.add_page()
    pdf.header_block("STARTUP INDIA CERTIFICATE", "DPIIT Recognition Certificate", (255, 87, 34))
    pdf.section("Recognition Details")
    if readable:
        pdf.field("Company", sc["company"])
        pdf.field("DPIIT Number", "DIPP" + sc["pan"][:6])
        pdf.field("Status", "Recognized")
    else:
        # Simulate unreadable scan
        pdf.body("[ Scan quality too low - text not extractable ]")
        pdf.body("DPIIT Number: [unreadable]  Name: [unreadable]")
    return _save_pdf(pdf, sc["scenario_id"], "startup_india")


DOC_GENERATORS = {
    "pan": _pan_pdf,
    "gst": _gst_pdf,
    "udyam": _udyam_pdf,
    "epfo": _epfo_pdf,
    "esic": _esic_pdf,
    "non_blacklisting": _non_bl_pdf,
    "oem_auth": _oem_pdf,
    "startup_india": lambda sc: _startup_pdf(sc, readable="startup_unverified" not in sc["anomalies"]),
}


def _generate_mock_portal_response(sc):
    """Generate a mock portal JSON response for this scenario."""
    gstin_active = "gst_inactive" not in sc["anomalies"]
    pan_match = "pan_gstin_mismatch" not in sc["anomalies"]

    response = {
        "scenario_id": sc["scenario_id"],
        "scenario_name": sc["name"],
        "pan": sc["pan"],
        "gstin": sc["gstin"],
        "note": "Mock portal response — not from authenticated government API",
        "adapters": {
            "pan_gstin_cross": {
                "verified": pan_match,
                "status": "match" if pan_match else "mismatch",
                "source": "offline_cross_check",
                "detail": "PAN matches GSTIN embedded PAN." if pan_match
                          else "PAN does NOT match GSTIN embedded PAN.",
            },
            "gstin_live_status": {
                "verified": gstin_active,
                "status": "active" if gstin_active else "cancelled",
                "source": "mock_gst_portal",
                "gst_status": "Active" if gstin_active else "Cancelled",
                "detail": f"GSTIN is {'Active' if gstin_active else 'Cancelled'} on GST portal.",
                "is_mock": True,
            },
            "epfo_compliance": {
                "verified": "epfo" in sc["docs"],
                "status": "needs_review" if "epfo" in sc["docs"] else "fail",
                "source": "mock_epfo_portal",
                "is_mock": True,
                "detail": "EPFO registration document uploaded and processed."
                if "epfo" in sc["docs"] else "EPFO registration document not uploaded.",
            },
            "esic_compliance": {
                "verified": "esic" in sc["docs"],
                "status": "needs_review" if "esic" in sc["docs"] else "fail",
                "source": "mock_esic_portal",
                "is_mock": True,
                "detail": "ESIC registration document uploaded and processed."
                if "esic" in sc["docs"] else "ESIC registration document not uploaded.",
            },
        },
    }
    return response


def main():
    parser = argparse.ArgumentParser(description="Generate GeMGuard AI synthetic data")
    parser.add_argument("--seed-db", action="store_true",
                        help="POST generated bidders to running backend at localhost:8000")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("  GeMGuard AI — Synthetic Data Generator")
    print(f"{'='*60}\n")

    # Generate bidder profiles
    bidders = _make_bidders(SCENARIOS)
    bidders_path = os.path.join(OUT, "bidders.json")
    with open(bidders_path, "w") as f:
        json.dump(bidders, f, indent=2)
    print(f"  [OK] {len(bidders)} bidder profiles -> {bidders_path}")

    # Generate PDFs and portal responses for each scenario
    for sc in SCENARIOS:
        print(f"\n  Scenario {sc['scenario_id']}: {sc['name']}")
        for doc_type in sc["docs"]:
            gen = DOC_GENERATORS.get(doc_type)
            if gen:
                try:
                    path = gen(sc)
                    print(f"    [OK] {doc_type}.pdf")
                except Exception as e:
                    print(f"    [WARN] {doc_type}.pdf - {e}")

        # Mock portal response JSON
        portal_resp = _generate_mock_portal_response(sc)
        portal_path = os.path.join(PORTAL_OUT, f"{sc['scenario_id']}_portal_response.json")
        with open(portal_path, "w") as f:
            json.dump(portal_resp, f, indent=2)
        print(f"    [OK] mock_portal_responses/{sc['scenario_id']}_portal_response.json")

    print(f"\n{'='*60}")
    print(f"  Generated {len(bidders)} bidders across {len(SCENARIOS)} scenarios")
    print(f"  Output: {OUT}")
    print(f"{'='*60}\n")

    if args.seed_db:
        _seed_db(bidders)


def _seed_db(bidders):
    """POST the first bidder of each scenario to the running backend."""
    try:
        import httpx
    except ImportError:
        print("  [SKIP] httpx not available. Install with: pip install httpx")
        return

    print("  Seeding database (first bidder per scenario)...")
    seen_scenarios = set()
    for b in bidders:
        if b["scenario_id"] in seen_scenarios:
            continue
        seen_scenarios.add(b["scenario_id"])
        try:
            resp = httpx.post("http://localhost:8000/bidders/", json={
                "company_name": b["company_name"],
                "company_type": b["company_type"],
                "pan_number": b["pan_number"],
                "gstin": b["gstin"],
                "udyam_number": b["udyam_number"],
            }, timeout=5.0)
            if resp.status_code in (200, 201):
                print(f"    [OK] Seeded: {b['company_name']} (scenario {b['scenario_id']})")
            else:
                print(f"    [FAIL] {b['company_name']}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"    [ERROR] {b['company_name']}: {e}")


if __name__ == "__main__":
    main()
