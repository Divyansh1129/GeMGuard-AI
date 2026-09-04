"""
report_generator.py
--------------------
Generates a downloadable PDF compliance report (dossier) for a bidder.
Uses fpdf2 for PDF generation.
"""

import os
from datetime import datetime
from fpdf import FPDF


class ComplianceReport(FPDF):
    """Custom PDF layout for compliance reports."""

    def header(self):
        self.set_fill_color(13, 71, 161)
        self.rect(0, 0, 210, 22, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 8, "GEMGUARD AI - COMPLIANCE VERIFICATION REPORT", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.cell(0, 4, f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M IST')}  |  Classification: OFFICIAL", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, "GeMGuard AI - AI-Powered Compliance Platform | Decision Support Only - Officer Authorization Required", align="C")
        self.ln(3)
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_header(self, title, color=(13, 71, 161)):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def field_row(self, label, value, bold_value=False):
        self.set_font("Helvetica", "", 9)
        self.cell(60, 6, label + ":", new_x="RIGHT")
        self.set_font("Helvetica", "B" if bold_value else "", 9)
        self.cell(0, 6, str(value or "N/A"), new_x="LMARGIN", new_y="NEXT")

    def status_badge(self, status):
        colors = {
            "pass": (27, 94, 32), "fail": (183, 28, 28),
            "needs_review": (230, 81, 0), "active": (27, 94, 32),
            "clean": (27, 94, 32), "blacklisted": (183, 28, 28),
        }
        labels = {
            "pass": "PASS", "fail": "FAIL", "needs_review": "REVIEW",
            "active": "ACTIVE", "clean": "CLEAR", "blacklisted": "BLACKLISTED",
        }
        color = colors.get(status, (100, 100, 100))
        label = labels.get(status, status.upper())
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8)
        self.cell(22, 5, f" {label} ", fill=True)
        self.set_text_color(0, 0, 0)

    def separator(self):
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)


def generate_compliance_report(
    bidder: dict,
    compliance_result: dict,
    document_results: list,
    govt_checks: dict = None,
    blacklist_result: dict = None,
    output_path: str = None,
) -> str:
    """
    Generate a PDF compliance report and return the file path.

    Args:
        bidder: dict with company_name, pan_number, gstin, etc.
        compliance_result: dict with compliance_score, risk_level, ai_recommendation
        document_results: list of DocumentVerificationResult dicts
        govt_checks: dict of government verification results
        blacklist_result: dict from blacklist_checker
        output_path: where to save the PDF (auto-generated if None)
    """
    if output_path is None:
        os.makedirs("reports", exist_ok=True)
        output_path = os.path.join(
            "reports",
            f"compliance_report_{bidder.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

    pdf = ComplianceReport()
    pdf.alias_nb_pages()
    pdf.add_page()

    # ── Bidder Summary ──────────────────────────────────────────
    pdf.section_header("BIDDER INFORMATION")
    pdf.field_row("Company Name", bidder.get("company_name"), bold_value=True)
    pdf.field_row("PAN", bidder.get("pan_number"))
    pdf.field_row("GSTIN", bidder.get("gstin"))
    pdf.field_row("Udyam Number", bidder.get("udyam_number"))
    pdf.field_row("Bidder ID", bidder.get("id"))
    pdf.field_row("Tender ID", bidder.get("tender_id"))
    pdf.ln(3)

    # ── Overall Compliance ─────────────────────────────────────
    pdf.section_header("OVERALL COMPLIANCE ASSESSMENT")
    score = compliance_result.get("compliance_score", 0)
    risk = compliance_result.get("risk_level", "Unknown")
    risk_colors = {"Low": (27, 94, 32), "Medium": (230, 81, 0), "High": (183, 28, 28)}

    pdf.set_font("Helvetica", "B", 20)
    score_color = (27, 94, 32) if score >= 80 else (230, 81, 0) if score >= 50 else (183, 28, 28)
    pdf.set_text_color(*score_color)
    pdf.cell(50, 12, f"{score}/100", new_x="RIGHT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(30, 12, "Compliance Score", new_x="RIGHT")

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*risk_colors.get(risk, (100, 100, 100)))
    pdf.cell(30, 12, risk, new_x="RIGHT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 12, "Risk Level", new_x="LMARGIN", new_y="NEXT")

    pdf.field_row("ML Risk Probability", f"{compliance_result.get('ml_risk_probability', 0):.1%}")
    pdf.ln(3)

    # ── Blacklist Check ────────────────────────────────────────
    if blacklist_result:
        pdf.section_header("BLACKLIST / DEBARMENT CHECK",
                          color=(183, 28, 28) if blacklist_result.get("status") == "blacklisted" else (27, 94, 32))
        pdf.set_font("Helvetica", "", 9)
        pdf.status_badge(blacklist_result.get("status", "clean"))
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(5, 5, " ")
        pdf.cell(0, 5, blacklist_result.get("detail", ""), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # ── Government Verification ────────────────────────────────
    if govt_checks:
        pdf.section_header("GOVERNMENT DATABASE VERIFICATION", color=(0, 77, 64))
        for check_name, check_result in govt_checks.items():
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(50, 6, check_name.replace("_", " ").title() + ":", new_x="RIGHT")
            status = "pass" if check_result.get("verified") else "fail"
            pdf.status_badge(status)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(5, 5, " ")
            detail = check_result.get("detail", "")
            if len(detail) > 80:
                detail = detail[:77] + "..."
            pdf.cell(0, 5, detail, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        pdf.ln(3)

    # ── Document-Level Results ─────────────────────────────────
    pdf.section_header("DOCUMENT VERIFICATION RESULTS")

    for doc_result in document_results:
        doc_type = doc_result.get("document_type", "unknown").upper()
        overall = doc_result.get("overall_status", "needs_review")
        score = doc_result.get("overall_score", 0)
        ext_conf = doc_result.get("extraction_confidence")

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(40, 6, doc_type, new_x="RIGHT")
        pdf.status_badge(overall)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(5, 5, " ")
        pdf.cell(30, 5, f"Score: {score}/100", new_x="RIGHT")
        ext_pct = f"{round(ext_conf * 100)}%" if ext_conf is not None else "N/A"
        pdf.cell(0, 5, f"OCR Confidence: {ext_pct}", new_x="LMARGIN", new_y="NEXT")

        # Field checks
        for check in doc_result.get("field_checks", []):
            pdf.set_font("Helvetica", "", 8)
            pdf.set_x(20)
            status_sym = {
                "pass": "[PASS]", "fail": "[FAIL]", "needs_review": "[REVIEW]"
            }.get(check["status"], "[?]")
            pdf.cell(0, 5,
                f"  {status_sym} {check['field_name']}: {check['reason']}",
                new_x="LMARGIN", new_y="NEXT",
            )

        pdf.separator()

    # ── AI Recommendation ──────────────────────────────────────
    pdf.section_header("AI-GENERATED RECOMMENDATION")
    pdf.set_font("Helvetica", "I", 9)
    recommendation = compliance_result.get("ai_recommendation", "No recommendation available.")
    pdf.multi_cell(0, 5, recommendation)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(0, 5, "DISCLAIMER: This is AI-generated decision support. Final authority rests with the designated procurement officer.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    # Save
    pdf.output(output_path)
    return output_path
