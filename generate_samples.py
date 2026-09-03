"""
Generate sample Indian procurement documents (PDF) for testing GeMGuard AI.
All documents use entity "TechNova Solutions Pvt. Ltd." with consistent
PAN/GSTIN/Udyam so cross-document checks pass.

Run:  python generate_samples.py
Output: sample_docs/ folder with 8 PDFs
"""
import os
from fpdf import FPDF

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_docs")
os.makedirs(OUT, exist_ok=True)

# ── Consistent entity data ──────────────────────────────────────────────
COMPANY  = "TechNova Solutions Pvt. Ltd."
PAN      = "AABCT1234E"
GSTIN    = "27AABCT1234E1ZP"
UDYAM    = "UDYAM-MH-26-0012345"
EPFO     = "MHPUN0012345000"
ESIC     = "31000123456789012"


class DocPDF(FPDF):
    """Helper for consistent look across all sample documents."""

    def header_block(self, title, subtitle="", color=(26, 35, 126)):
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
        self.set_fill_color(232, 234, 246)
        self.cell(0, 9, "  " + heading, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def field(self, label, value):
        self.set_font("Helvetica", "", 11)
        self.cell(80, 7, label + ":", new_x="RIGHT")
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def separator(self):
        self.set_draw_color(189, 189, 189)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer_note(self, text):
        self.set_y(-25)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 5, text, align="C")
        self.set_text_color(0, 0, 0)


def save(pdf, filename):
    path = os.path.join(OUT, filename)
    pdf.output(path)
    print(f"  OK: {filename}")


# =====================================================================
# 1. PAN Card
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("INCOME TAX DEPARTMENT", "Government of India - PAN Card", (26, 35, 126))
pdf.section("Permanent Account Number")
pdf.field("PAN", PAN)
pdf.field("Name", COMPANY)
pdf.field("Legal Name", COMPANY)
pdf.field("Status", "Company")
pdf.field("Date of Incorporation", "15/03/2018")
pdf.ln(4)
pdf.separator()
pdf.section("Additional Details")
pdf.field("Jurisdiction", "CIT Mumbai  6(1)")
pdf.field("AO Code", "MUM/W/06/1")
pdf.field("Father's Name / Org", "Not Applicable (Company)")
pdf.footer_note("Issued by: Income Tax Department, Government of India. Valid for lifetime of PAN holder.")
save(pdf, "pan_card.pdf")

# =====================================================================
# 2. GST Certificate
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("GOODS AND SERVICES TAX", "Registration Certificate - Form GST REG-06", (0, 77, 64))
pdf.section("GST Registration Details")
pdf.field("GSTIN", GSTIN)
pdf.field("Legal Name", COMPANY)
pdf.field("Trade Name", "TechNova Solutions")
pdf.field("PAN", PAN)
pdf.field("State", "Maharashtra (27)")
pdf.field("Centre Jurisdiction", "Mumbai South")
pdf.field("State Jurisdiction", "Division III")
pdf.ln(4)
pdf.separator()
pdf.section("Registration Information")
pdf.field("Date of Registration", "01/04/2018")
pdf.field("Constitution", "Private Limited Company")
pdf.field("Taxpayer Type", "Regular")
pdf.field("Status", "Active")
pdf.field("Valid From", "01/04/2018")
pdf.field("Principal Place", "Plot 42, Hinjewadi Phase 2, Pune 411057")
pdf.footer_note("Issued by: Central Board of Indirect Taxes and Customs, Ministry of Finance")
save(pdf, "gst_certificate.pdf")

# =====================================================================
# 3. Udyam Certificate
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("UDYAM REGISTRATION", "Ministry of Micro, Small and Medium Enterprises", (230, 81, 0))
pdf.section("Udyam Registration Certificate")
pdf.field("Udyam Registration Number", UDYAM)
pdf.field("Name of Enterprise", COMPANY)
pdf.field("Legal Name", COMPANY)
pdf.field("Type of Enterprise", "Micro")
pdf.field("Major Activity", "Services - IT Consulting")
pdf.field("Social Category", "General")
pdf.field("Date of Incorporation", "15/03/2018")
pdf.ln(4)
pdf.separator()
pdf.section("Enterprise Details")
pdf.field("PAN", PAN)
pdf.field("Date of Udyam Registration", "22/07/2020")
pdf.field("District", "Pune")
pdf.field("State", "Maharashtra")
pdf.field("Flat/Building", "Plot 42, TechPark, Hinjewadi Phase 2")
pdf.field("PIN Code", "411057")
pdf.field("Mobile", "9876543210")
pdf.field("Email", "info@technova.co.in")
pdf.footer_note("Issued by: Ministry of MSME, Government of India - udyamregistration.gov.in")
save(pdf, "udyam_certificate.pdf")

# =====================================================================
# 4. EPFO Registration
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("EPFO REGISTRATION", "Employees' Provident Fund Organisation", (27, 94, 32))
pdf.section("Establishment Registration Certificate")
pdf.field("Establishment Code", EPFO)
pdf.field("Name of Establishment", COMPANY)
pdf.field("Legal Name", COMPANY)
pdf.field("PAN", PAN)
pdf.field("Coverage Date", "01/06/2019")
pdf.ln(4)
pdf.separator()
pdf.section("Establishment Details")
pdf.field("Address", "Plot 42, Hinjewadi Phase 2, Pune 411057")
pdf.field("District", "Pune")
pdf.field("State", "Maharashtra")
pdf.field("Number of Employees", "28")
pdf.field("Employer Category", "Private Sector - IT Services")
pdf.ln(4)
pdf.separator()
pdf.section("Compliance Status")
pdf.field("Status", "Active and Compliant")
pdf.field("Last ECR Filed", "June 2026")
pdf.field("Last Payment Date", "15/07/2026")
pdf.field("Total PF Balance", "INR 42,18,650")
pdf.footer_note("Issued by: EPFO, Ministry of Labour and Employment, Government of India")
save(pdf, "epfo_registration.pdf")

# =====================================================================
# 5. ESIC Registration
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("ESIC REGISTRATION", "Employees' State Insurance Corporation", (136, 14, 79))
pdf.section("Employer Registration Certificate")
pdf.field("ESIC Code", ESIC)
pdf.field("Name of Employer", COMPANY)
pdf.field("Legal Name", COMPANY)
pdf.field("PAN", PAN)
pdf.field("Coverage Date", "01/06/2019")
pdf.ln(4)
pdf.separator()
pdf.section("Employer Details")
pdf.field("Address", "Plot 42, Hinjewadi Phase 2, Pune 411057")
pdf.field("Local Office", "Pune")
pdf.field("Region", "Maharashtra")
pdf.field("Number of Employees", "28")
pdf.ln(4)
pdf.separator()
pdf.section("Contribution Status")
pdf.field("Status", "Active")
pdf.field("Last Contribution Month", "June 2026")
pdf.field("Last Payment Date", "15/07/2026")
pdf.footer_note("Issued by: ESIC, Ministry of Labour and Employment, Government of India")
save(pdf, "esic_registration.pdf")

# =====================================================================
# 6. Non-Blacklisting Declaration
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("SELF-DECLARATION", "Non-Blacklisting / Non-Debarment Affidavit", (55, 71, 79))
pdf.section("Declaration Details")
pdf.field("Company", COMPANY)
pdf.field("Legal Name", COMPANY)
pdf.field("PAN", PAN)
pdf.field("GSTIN", GSTIN)
pdf.field("Date", "01/09/2026")
pdf.field("Place", "Pune, Maharashtra")
pdf.ln(4)
pdf.separator()
pdf.section("Self-Declaration")
pdf.body_text(
    f"I, Rajesh Kumar, Director of {COMPANY}, do hereby solemnly declare and certify the following:\n\n"
    f"1. {COMPANY} has NOT been blacklisted or debarred by any Central Government, "
    "State Government department, or any Public Sector Undertaking (PSU) in India.\n\n"
    "2. No proceedings for blacklisting or debarment are currently pending against the company "
    "before any authority.\n\n"
    "3. The company has not been convicted of any criminal offence related to business or professional conduct.\n\n"
    "4. This declaration is true and correct to the best of my knowledge and belief. "
    "I understand that furnishing false information may lead to disqualification and legal action."
)
pdf.ln(8)
pdf.body_text("Authorized Signatory: Rajesh Kumar, Director")
pdf.body_text(f"For and on behalf of: {COMPANY}")
pdf.footer_note("Self-declaration as per GeM procurement guidelines")
save(pdf, "non_blacklisting.pdf")

# =====================================================================
# 7. OEM Authorization Letter
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("OEM AUTHORIZATION", "Original Equipment Manufacturer Certificate", (74, 20, 140))
pdf.section("Issuing OEM")
pdf.field("OEM Name", "GlobalTech Systems Inc.")
pdf.field("Address", "1200 Innovation Drive, San Jose, CA 95134, USA")
pdf.field("Contact", "partnerships@globaltech.com")
pdf.ln(4)
pdf.separator()
pdf.section("Authorization Details")
pdf.body_text("To Whom It May Concern,")
pdf.body_text(
    f"This is to certify that {COMPANY} (PAN: {PAN}) is an Authorized Reseller "
    "and System Integrator for GlobalTech Systems products in the territory of India."
)
pdf.ln(2)
pdf.field("Authorized Entity", COMPANY)
pdf.field("Legal Name", COMPANY)
pdf.field("PAN", PAN)
pdf.field("Product Lines", "Enterprise Servers, Storage Arrays, Network Switches")
pdf.field("Territory", "Republic of India")
pdf.field("Authorization Level", "Platinum Partner")
pdf.field("Valid From", "01/01/2026")
pdf.field("Valid Until", "31/12/2026")
pdf.ln(4)
pdf.separator()
pdf.body_text("This letter is issued at the request of the authorized entity for the purpose of "
              "participating in Government e-Marketplace (GeM) procurement tenders.")
pdf.ln(4)
pdf.body_text("John Mitchell\nVP Global Partnerships\nGlobalTech Systems Inc.")
pdf.footer_note("OEM Authorization Letter - valid for GeM procurement only")
save(pdf, "oem_authorization.pdf")

# =====================================================================
# 8. Sample Tender Document
# =====================================================================
pdf = DocPDF()
pdf.add_page()
pdf.header_block("GOVERNMENT e-MARKETPLACE", "Tender Document - Ministry of Electronics and IT", (13, 71, 161))
pdf.section("Tender Information")
pdf.field("Tender ID", "GEM/2026/B/4567890")
pdf.field("Department", "Ministry of Electronics and IT")
pdf.field("Category", "IT Hardware and Services")
pdf.field("Estimated Value", "INR 2,50,00,000")
pdf.field("Bid Submission Deadline", "30/09/2026, 17:00 IST")
pdf.field("Technical Evaluation", "05/10/2026")
pdf.ln(4)
pdf.separator()
pdf.section("Eligibility Criteria")
pdf.body_text(
    "The bidder must meet ALL of the following eligibility requirements to qualify:\n\n"
    "1. Must hold a valid PAN issued by the Income Tax Department.\n"
    "2. Must have active GST Registration (GSTIN required).\n"
    "3. Must have valid Udyam / MSME Registration Certificate.\n"
    "4. Must have EPFO Registration (mandatory for establishments with 20+ employees).\n"
    "5. Must have ESIC Registration (mandatory for covered establishments).\n"
    "6. Must submit a Non-Blacklisting / Non-Debarment Self-Declaration.\n"
    "7. Must provide OEM Authorization Letter for the quoted products.\n"
    "8. Startup India Certificate (optional, for additional preference)."
)
pdf.ln(4)
pdf.separator()
pdf.section("Additional Requirements")
pdf.field("Make in India Local Content", "50%")
pdf.field("Minimum Annual Turnover", "INR 1 Crore")
pdf.field("Experience", "3 years in IT infrastructure supply")
pdf.field("Quality Certification", "ISO 9001:2015 preferred")
pdf.ln(4)
pdf.separator()
pdf.section("Scope of Work")
pdf.body_text(
    "Supply, installation, and commissioning of IT infrastructure including:\n"
    "- 50 Enterprise-grade servers\n"
    "- 10 Storage arrays (minimum 100TB each)\n"
    "- Network switches and cabling\n"
    "- 3 years Annual Maintenance Contract (AMC)\n"
    "- On-site support within 4 hours of reported incident"
)
pdf.footer_note("Government e-Marketplace - gem.gov.in - Tender Document")
save(pdf, "sample_tender.pdf")


# -- Summary --
print(f"\n{'='*60}")
print(f"  All 8 PDFs created in: {os.path.abspath(OUT)}")
print(f"{'='*60}")
print(f"""
  Entity:  {COMPANY}
  PAN:     {PAN}
  GSTIN:   {GSTIN}
  Udyam:   {UDYAM}

  UPLOAD ORDER:
  -------------
  1. Upload tender first:    sample_tender.pdf
     (Dashboard > Upload Tender)

  2. Create a bidder with:
     Company Name:  {COMPANY}
     PAN:           {PAN}
     GSTIN:         {GSTIN}
     Udyam:         {UDYAM}

  3. Upload docs for the bidder:
     pan_card.pdf            -> type: pan
     gst_certificate.pdf     -> type: gst
     udyam_certificate.pdf   -> type: udyam
     epfo_registration.pdf   -> type: epfo
     esic_registration.pdf   -> type: esic
     non_blacklisting.pdf    -> type: non_blacklisting
     oem_authorization.pdf   -> type: oem_auth

  4. Run compliance check -> see separate Compliance Score
     vs Extraction Confidence in the UI!
""")

