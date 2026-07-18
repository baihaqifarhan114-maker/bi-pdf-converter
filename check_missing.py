"""Check why PRASTYO ARI WIBOWO has no credit limit."""
import pdfplumber

pdf = pdfplumber.open(r"C:\Users\baiha\Downloads\BANK INDONESIA - 10 Juni 2026.pdf")

for i, page in enumerate(pdf.pages):
    text = page.extract_text() or ""
    if 'PRASTYO ARI WIBOWO' in text and 'Gunakanlah kemudahan' in text:
        lines = text.split('\n')
        print(f"=== Page {i+1} ===")
        for j, line in enumerate(lines):
            print(f"  {j:3d}: {line}")
        break
