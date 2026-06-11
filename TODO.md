# TODO — IHSG Dashboard (price-only heuristic)

## Backend
- [ ] Tambahkan utilitas di `bi_engine.py` untuk:
  - [ ] definisikan `normalize_id_ticker()` (mis. {BBCA -> BBCA.JK jika dipakai yfinance})
  - [ ] ambil universe IHSG dari sumber berbasis web (price-only), atau fallback hardcode list saat sumber gagal
  - [ ] hitung metrik momentum/drawdown/volatilitas dari price history
  - [ ] definisikan label kategori dengan heuristik berbasis metrik harga saja:
    - [ ] top gainers (return positif tertinggi)
    - [ ] top losers (return negatif terterendah)
    - [ ] growth vs value (proxy: growth = momentum kuat, value = relatif murah vs momentum; pakai proxy PE/PB tidak tersedia → gunakan proxy berbasis harga/volatilitas)
    - [ ] bullish vs bearish (proxy: return + sentiment optional/diabaikan di batch)
    - [ ] multibagger vs bagholder (proxy: multi-period return tinggi vs drawdown panjang)
    - [ ] value trap (proxy: murah tapi underperforming beberapa window)
    - [ ] zombie (proxy: sideways/low-return + volatilitas rendah/kehilangan momentum)
  - [ ] bentuk output payload terstruktur untuk frontend

- [ ] Tambahkan endpoint baru di `api_server.py`:
  - [ ] `GET /api/ihsg-dashboard?window_days=90&top_n=5&price_horizon_days=200`
  - [ ] return payload: kategori -> daftar 5 saham

## Frontend
- [ ] Tambahkan fungsi API client di `frontend/lib/api.js` untuk memanggil endpoint dashboard.
- [ ] Buat komponen `frontend/app/components/IhsgDashboard.jsx`:
  - [ ] UI tab kategori atau grid per kategori
  - [ ] render list saham per kategori (ticker + skor + persentase)
  - [ ] (opsional) chart agregat per kategori
- [ ] Update `frontend/app/page.jsx`:
  - [ ] tambahkan switch mode: `Single Ticker` vs `IHSG Dashboard`

## Testing
- [ ] Jalankan backend dan validasi endpoint `GET /api/ihsg-dashboard` mengembalikan struktur yang benar.
- [ ] Jalankan frontend dan pastikan render tidak error.
- [ ] Sesuaikan heuristik jika kategori tidak “masuk akal” untuk data yfinance.

