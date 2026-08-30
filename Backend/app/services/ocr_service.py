"""
ocr_service.py
---------------
Extracts raw text from uploaded documents (PDFs / images) BEFORE we send that
text to the LLM for structured field extraction.

Two cases:
  1. Text-based PDF (most GST/Udyam certs downloaded from portals) -> pdfplumber, fast & free
  2. Scanned image / photo of a document -> pytesseract (Tesseract OCR)
"""

import pdfplumber
try:
    import pymupdf
except ImportError:  # dependency is declared in requirements; keep text-PDF processing available until installed
    pymupdf = None
from PIL import Image
import pytesseract
import os

# Windows-specific: tell pytesseract exactly where Tesseract.exe is installed,
# since it's not automatically on the system PATH.
if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext in (".png", ".jpg", ".jpeg"):
        return _extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_from_pdf(file_path: str) -> str:
    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    text = "\n".join(text_chunks).strip()
    if text:
        return text
    # Scanned PDFs have no text layer. Render each real page and OCR it.
    if pymupdf is None:
        raise RuntimeError("PyMuPDF is required to OCR scanned PDFs. Install Backend/requirements.txt.")
    document = pymupdf.open(file_path)
    try:
        pages = []
        for page in document:
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pages.append(pytesseract.image_to_string(image))
        return "\n".join(pages).strip()
    finally:
        document.close()


def _extract_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)
