"""Quick check: extract credit limits from first 10 main pages."""
import pdfplumber, re

pdf = pdfplumber.open(r"C:\Users\baiha\Downloads\BANK INDONESIA - 10 Juni 2026.pdf")
pat = re.compile(r'^([\d,]+)\s+([\d,]+)\s+\d+\s+LANCAR', re.MULTILINE)

count = 0
for i, page in enumerate(pdf.pages):
    text = page.extract_text() or ""
    if 'Gunakanlah kemudahan' not in text:
        continue  # skip continuation pages
    m = pat.search(text)
    if m:
        print(f"Page {i+1}: Limit = {m.group(1)}, Sisa = {m.group(2)}")
    else:
        print(f"Page {i+1}: NO MATCH")
    count += 1
    if count >= 10:
        break
