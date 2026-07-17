"""Verify parser output accuracy against known data from PDF analysis."""
from parser import parse_pdf

pdf_path = r"C:\Users\baiha\Downloads\BANK INDONESIA - 10 Juni 2026.pdf"
records = parse_pdf(pdf_path)

# Create lookup by name
by_name = {r.nama: r for r in records}

# ── Test 1: AGUNG HARTONO (simple case) ──
print("=" * 60)
print("TEST 1: AGUNG HARTONO")
r = by_name.get('AGUNG HARTONO')
if r:
    print(f"  Card: {r.nomor_kartu}")
    print(f"  Tagihan Bulan Lalu: {r.tagihan_bulan_lalu:,.0f} {'CR' if r.tagihan_bulan_lalu_cr else 'DB'}")
    print(f"  Sub-Total: {r.sub_total:,.0f} {'CR' if r.sub_total_cr else 'DB'}")
    print(f"  Transactions ({len(r.transactions)}):")
    for tx in r.transactions:
        cr = ' CR' if tx.is_credit else ''
        print(f"    {tx.tanggal_transaksi} | {tx.tanggal_pembukuan} | {tx.keterangan[:40]:<40} | {tx.jumlah:>15,.0f}{cr}")
    # Expected: card 4895-9403-0012-6163, 7 transactions, tagihan 80,564,800
    assert r.nomor_kartu == '4895-9403-0012-6163', f"Card mismatch: {r.nomor_kartu}"
    assert r.tagihan_bulan_lalu == 80564800, f"Tagihan mismatch: {r.tagihan_bulan_lalu}"
    assert len(r.transactions) == 7, f"Tx count mismatch: {len(r.transactions)}"
    print("  ✅ PASSED")

# ── Test 2: AMALIA YUSTICIA TRI D (multi-line + cross-page) ──
print("\n" + "=" * 60)
print("TEST 2: AMALIA YUSTICIA TRI D (multi-line + cross-page)")
r = by_name.get('AMALIA YUSTICIA TRI D')
if r:
    print(f"  Card: {r.nomor_kartu}")
    print(f"  Tagihan Bulan Lalu: {r.tagihan_bulan_lalu:,.0f}")
    print(f"  Sub-Total: {r.sub_total:,.0f}")
    print(f"  Transactions ({len(r.transactions)}):")
    for tx in r.transactions:
        cr = ' CR' if tx.is_credit else ''
        desc_preview = tx.keterangan.replace('\n', ' | ')[:60]
        print(f"    {tx.tanggal_transaksi} | {tx.tanggal_pembukuan} | {desc_preview:<60} | {tx.jumlah:>15,.0f}{cr}")
    
    # Check multi-line descriptions
    multi_line_txs = [tx for tx in r.transactions if '\n' in tx.keterangan]
    print(f"\n  Multi-line descriptions: {len(multi_line_txs)}")
    for tx in multi_line_txs:
        print(f"    Description lines:")
        for line in tx.keterangan.split('\n'):
            print(f"      > {line}")
    
    # Expected: card 4340-7503-0012-4592, tagihan 46,790,234
    assert r.nomor_kartu == '4340-7503-0012-4592', f"Card mismatch: {r.nomor_kartu}"
    assert r.tagihan_bulan_lalu == 46790234, f"Tagihan mismatch: {r.tagihan_bulan_lalu}"
    # Should have 8 transactions (6 on page 3 + PAYMENT + STAMP DUTY on page 4)
    assert len(r.transactions) == 8, f"Tx count mismatch: {len(r.transactions)} (expected 8)"
    # Check cross-page: STAMP DUTY should be present (from page 4)
    stamp = [tx for tx in r.transactions if 'STAMP DUTY' in tx.keterangan]
    assert len(stamp) == 1, f"STAMP DUTY not found in cross-page data"
    print("  ✅ PASSED")

# ── Test 3: ABUDAUD GAMGULU (with currency conversion) ──
print("\n" + "=" * 60)
print("TEST 3: ABUDAUD GAMGULU")
r = by_name.get('ABUDAUD GAMGULU')
if r:
    print(f"  Card: {r.nomor_kartu}")
    print(f"  Transactions: {len(r.transactions)}")
    # Check QUIZIZZ transaction with USD/Kurs multi-line
    quizizz = [tx for tx in r.transactions if 'QUIZIZZ' in tx.keterangan]
    if quizizz:
        print(f"\n  QUIZIZZ transaction description:")
        for line in quizizz[0].keterangan.split('\n'):
            print(f"    > {line}")
        assert 'USD 600.00' in quizizz[0].keterangan, "USD info missing from multi-line"
        assert 'Kurs' in quizizz[0].keterangan, "Kurs info missing from multi-line"
        print("  ✅ Multi-line description correctly merged")
    print("  ✅ PASSED")

# ── Test 4: Last cardholder (ZULFENI WIDIASARI - cross-page page 180→181) ──
print("\n" + "=" * 60)
print("TEST 4: ZULFENI WIDIASARI (last cardholder, cross-page 180→181)")
r = by_name.get('ZULFENI WIDIASARI')
if r:
    print(f"  Card: {r.nomor_kartu}")
    print(f"  Transactions: {len(r.transactions)}")
    print(f"  Sub-Total: {r.sub_total:,.0f}")
    # Page 180 has 17 transactions + "Transaksi di lanjutkan ke halaman berikutnya"
    # Page 181 has 15 more transactions (including STAMP DUTY, SUB-TOTAL)
    # Total should be 17 + 14 transaction lines (excluding SUB-TOTAL) = ~31
    stamp = [tx for tx in r.transactions if 'STAMP DUTY' in tx.keterangan]
    payment = [tx for tx in r.transactions if 'PAYMENT' in tx.keterangan]
    assert len(stamp) == 1, f"STAMP DUTY count: {len(stamp)}"
    assert len(payment) >= 1, f"No PAYMENT found"
    assert r.sub_total == 20806562, f"Sub-total mismatch: {r.sub_total}"
    print("  ✅ PASSED")

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✅")
