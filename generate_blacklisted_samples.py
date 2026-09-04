"""
Generate failing/blacklisted sample Indian procurement documents (PDF) for testing GeMGuard AI.
Uses entity "Fraudtech Solutions Pvt. Ltd." (PAN: AABCF9999Z) which is present in the blacklist database!
"""
import os
from fpdf import FPDF

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_docs", "blacklisted_bidder")
os.makedirs(OUT, exist_ok=True)

COMPANY = "Fraudtech Solutions Pvt. Ltd."
PAN     = "AABCF9999Z"
GSTIN   = "27AABCF9999Z1ZQ"
UDYAM   = "UDYAM-MH-26-0099999"

class DocPDF(FPDF):
    def header_block(self, title, subtitle="", color=(183, 28, 28)):
        self.set_fill_color(*color)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        if subtitle:
            self.set_font("Helvetica", "", 10)
            self.cell(0, 5, subtitle, new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_text_color(0, 0, 0)

    def section(self, heading):
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(255, 235, 238)
        self.cell(0, 9, "  " + heading, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def field(self, label, value):
        self.set_font("Helvetica", "", 11)
        self.cell(80, 7, label + ":", new_x="RIGHT")
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

def save(pdf, filename):
    path = os.path.join(OUT, filename)
    pdf.output(path)
    print(f"  OK: {filename}")

# PAN Card
pdf = DocPDF()
pdf.add_page()
pdf.header_block("INCOME TAX DEPARTMENT", "Government of India - PAN Card", (183, 28, 28))
pdf.section("Permanent Account Number")
pdf.field("PAN", PAN)
pdf.field("Name", COMPANY)
pdf.field("Legal Name", COMPANY)
pdf.field("Status", "Company")
save(pdf, "blacklisted_pan_card.pdf")

# GST Certificate
pdf = DocPDF()
pdf.add_page()
pdf.header_block("GOODS AND SERVICES TAX", "Registration Certificate", (183, 28, 28))
pdf.section("GST Registration Details")
pdf.field("GSTIN", GSTIN)
pdf.field("Legal Name", COMPANY)
pdf.field("PAN", PAN)
pdf.field("Status", "Suspended")
save(pdf, "blacklisted_gst_certificate.pdf")

print(f"\nCreated blacklisted bidder PDFs in {OUT}")
