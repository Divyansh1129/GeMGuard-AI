"""
report_generator.py
--------------------
Generates a downloadable PDF compliance report (dossier) for a bidder.
Uses fpdf2 for PDF generation with full ASCII text sanitization to prevent unicode errors.
"""

import os
from datetime import datetime
from fpdf import FPDF


def _clean(text: str) -> str:
    """Sanitize text to latin-1 to prevent fpdf2 encoding errors."""
    if not text:
        return ""
    s = str(text)
    s = s.replace("—", "-").replace("–", "-").replace("’", "'").replace("“", '"').replace("”", '"').replace("✓", "[OK]")
    return s.encode("latin-1", errors="replace").decode("latin-1")


class ComplianceReport(FPDF):
    """Custom PDF layout for compliance reports."""

    def header(self):
        self.set_fill_color(13, 71, 161)
        self.rect(0, 0, 210, 22, "F")
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 8, _clean("GEMGUARD AI - COMPLIANCE VERIFICATION DOSSIER"), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.cell(0, 4, _clean(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M IST')}  |  Classification: OFFICIAL DECISION SUPPORT"), new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, _clean("GeMGuard AI Platform | Decision Support Tool - Officer Authorization Required"), align="C")
        self.ln(3)
        self.cell(0, 4, _clean(f"Page {self.page_no()}/{{nb}}"), align="C")

    def section_header(self, title, color=(13, 71, 161)):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, _clean(f"  {title}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def field_row(self, label, value, bold_value=False):
        self.set_font("Helvetica", "", 9)
        self.cell(65, 6, _clean(label) + ":", new_x="RIGHT")
        self.set_font("Helvetica", "B" if bold_value else "", 9)
        self.cell(0, 6, _clean(str(value or "N/A")), new_x="LMARGIN", new_y="NEXT")

    def status_badge(self, status):
        colors = {
            "pass": (27, 94, 32), "fail": (183, 28, 28),
            "needs_review": (230, 81, 0), "active": (27, 94, 32),
            "clean": (27, 94, 32), "blacklisted": (183, 28, 28),
        }
        labels = {
            "pass": "PASS", "fail": "FAIL", "needs_review": "PENDING AUTH",
            "active": "ACTIVE", "clean": "CLEAR", "blacklisted": "BLACKLISTED",
        }
        color = colors.get(status, (100, 100, 100))
        label = labels.get(status, status.upper())
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8)
        self.cell(26, 5, _clean(f" {label} "), fill=True)
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
    pdf.section_header("BIDDER SUMMARY INFORMATION")
    pdf.field_row("Company Name", bidder.get("company_name"), bold_value=True)
    pdf.field_row("PAN Number", bidder.get("pan_number"))
    pdf.field_row("GSTIN Number", bidder.get("gstin"))
    pdf.field_row("Udyam Number", bidder.get("udyam_number"))
    pdf.field_row("Bidder System ID", bidder.get("id"))
    pdf.field_row("Linked Tender ID", bidder.get("tender_id"))
    pdf.ln(3)

    # ── Overall Compliance ─────────────────────────────────────
    pdf.section_header("OVERALL COMPLIANCE EVALUATION")
    score = compliance_result.get("compliance_score", 0)
    risk = compliance_result.get("risk_level", "Unknown")
    risk_colors = {"Low": (27, 94, 32), "Medium": (230, 81, 0), "High": (183, 28, 28)}

    pdf.set_font("Helvetica", "B", 20)
    score_color = (27, 94, 32) if score >= 85 else (230, 81, 0) if score >= 50 else (183, 28, 28)
    pdf.set_text_color(*score_color)
    pdf.cell(50, 12, _clean(f"{score}/100"), new_x="RIGHT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(30, 12, _clean("Compliance Score"), new_x="RIGHT")

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*risk_colors.get(risk, (100, 100, 100)))
    pdf.cell(30, 12, _clean(risk), new_x="RIGHT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 12, _clean("Risk Level"), new_x="LMARGIN", new_y="NEXT")

    pdf.field_row("ML Risk Probability", _clean(f"{compliance_result.get('ml_risk_probability', 0):.1%}"))
    pdf.ln(3)

    # ── Blacklist Check ────────────────────────────────────────
    if blacklist_result:
        pdf.section_header(
            "CVC / GEM BLACKLIST CHECK",
            color=(183, 28, 28) if blacklist_result.get("status") == "blacklisted" else (27, 94, 32),
        )
        pdf.status_badge(blacklist_result.get("status", "clean"))
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(5, 5, " ")
        pdf.cell(0, 5, _clean(blacklist_result.get("detail", "")), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # ── Government Verification ────────────────────────────────
    if govt_checks:
        pdf.section_header("GOVERNMENT PORTAL API VERIFICATION", color=(0, 77, 64))
        for check_name, check_result in govt_checks.items():
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(55, 6, _clean(check_name.replace("_", " ").title()) + ":", new_x="RIGHT")
            status = "pass" if check_result.get("verified") else "fail"
            pdf.status_badge(status)
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(5, 5, " ")
            detail = _clean(check_result.get("detail", ""))
            if len(detail) > 75:
                detail = detail[:72] + "..."
            pdf.cell(0, 5, detail, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        pdf.ln(3)

    # ── Document-Level Results ─────────────────────────────────
    pdf.section_header("EVIDENCE DOCUMENT VERIFICATION FINDINGS")

    for doc_result in document_results:
        doc_type = doc_result.get("document_type", "unknown").upper()
        overall = doc_result.get("overall_status", "needs_review")
        score = doc_result.get("overall_score", 0)
        ext_conf = doc_result.get("extraction_confidence")

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(40, 6, _clean(doc_type), new_x="RIGHT")
        pdf.status_badge(overall)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(5, 5, " ")
        pdf.cell(30, 5, _clean(f"Score: {score}/100"), new_x="RIGHT")
        ext_pct = f"{round(ext_conf * 100)}%" if ext_conf is not None else "N/A"
        pdf.cell(0, 5, _clean(f"OCR Confidence: {ext_pct}"), new_x="LMARGIN", new_y="NEXT")

        for check in doc_result.get("field_checks", []):
            pdf.set_font("Helvetica", "", 8)
            pdf.set_x(20)
            status_sym = {
                "pass": "[PASS]", "fail": "[FAIL]", "needs_review": "[PENDING AUTH]"
            }.get(check["status"], "[?]")
            pdf.cell(
                0, 5,
                _clean(f"  {status_sym} {check['field_name']}: {check['reason']}"),
                new_x="LMARGIN", new_y="NEXT",
            )

        pdf.separator()

    # ── AI Recommendation ──────────────────────────────────────
    pdf.section_header("AI COMPLIANCE ASSESSMENT & RECOMMENDATION")
    pdf.set_font("Helvetica", "", 9)
    recommendation = _clean(compliance_result.get("ai_recommendation", "No recommendation available."))
    pdf.multi_cell(0, 5, recommendation)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(0, 5, _clean("DISCLAIMER: Decision support tool. Final legal authority rests with the designated Procurement Officer."),
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    # Save
    pdf.output(output_path)
    return output_path
