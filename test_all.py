"""Test all 4 PDFs to verify parser works on each one."""
import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')

from parser import parse_pdf, generate_excel

pdfs = [
    r"C:\Users\baiha\Downloads\Februari 2026.pdf",
    r"C:\Users\baiha\Downloads\Maret 2026.pdf",
    r"C:\Users\baiha\Downloads\April 2026.pdf",
    r"C:\Users\baiha\Downloads\Mei 2026.pdf",
]

for pdf_path in pdfs:
    name = os.path.basename(pdf_path)
    if not os.path.exists(pdf_path):
        print(f"[SKIP] {name} - file not found")
        continue
    
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        t0 = time.time()
        records = parse_pdf(pdf_path)
        t1 = time.time()
        
        no_limit = [r for r in records if r.limit_kartu_kredit is None]
        total_tx = sum(len(r.transactions) for r in records)
        
        print(f"  Parse time: {t1-t0:.1f}s")
        print(f"  Cardholders: {len(records)}")
        print(f"  Transactions: {total_tx}")
        print(f"  With limit: {len(records)-len(no_limit)}, Missing: {len(no_limit)}")
        
        if no_limit:
            for r in no_limit:
                print(f"    MISSING LIMIT: {r.nama}")
        
        # Try generating Excel
        out_path = os.path.join("outputs", f"test_{name.replace('.pdf', '.xlsx')}")
        os.makedirs("outputs", exist_ok=True)
        stats = generate_excel(records, out_path)
        print(f"  Excel: OK ({stats['total_rows']} rows)")
        print(f"  RESULT: PASS")
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        print(f"  RESULT: FAIL")
