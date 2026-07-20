"""Compare text extraction output: pdfplumber vs PyMuPDF."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"C:\Users\baiha\Downloads\Februari 2026.pdf"

# ── PyMuPDF (fitz) ──
import fitz
doc = fitz.open(pdf_path)
page = doc[0]
fitz_text = page.get_text()
doc.close()

print("=" * 60)
print("PyMuPDF (fitz) - Page 1")
print("=" * 60)
for i, line in enumerate(fitz_text.split('\n')[:50]):
    print(f"  {i:3d}: {line}")

print()

# ── pdfplumber ──
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    plumber_text = pdf.pages[0].extract_text()

print("=" * 60)
print("pdfplumber - Page 1")
print("=" * 60)
for i, line in enumerate(plumber_text.split('\n')[:50]):
    print(f"  {i:3d}: {line}")
