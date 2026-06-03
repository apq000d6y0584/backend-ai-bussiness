# TODO_VISUALISASI — Visualisasi lanjutan

## Target fitur
1. Chart sentiment: timeline/bar “sentimen tiap headline” (atau agregasi per batch).
2. Highlight top headline: headline teratas dipilih berdasarkan mapped_score positif/negatif.
3. Band risk/volatility: tambah metrik dari harga (range/standard deviation 7 hari).

## Rencana implementasi (backend + frontend)

### Backend (bi_engine.py)
- [ ] Keluarkan metrik sentiment per headline dalam payload yang sudah ada.
- [ ] Hitung “top headline” berdasarkan mapped_score absolut (atau berdasarkan tanda positif/negatif terkuat).
- [ ] Hitung metrik volatilitas berbasis 7 hari: range (max-min) dan std dev (atau std dari returns) dan expose di payload.
- [ ] Pastikan nama field konsisten dengan frontend (mis. `sentiment_headlines`, `top_headline`, `volatility_metrics`).

### API layer (api_server.py)
- [ ] Pastikan endpoint `/api/bi` mengembalikan field baru tersebut dalam `data`.

### Frontend
- [ ] Buat komponen chart baru: `SentimentTimelineChart.jsx` (pakai recharts agar konsisten dengan PriceChart).
- [ ] Buat metrik band risk/volatility: komponen ringan (mis. dalam `PriceChart` card atau komponen baru `VolatilityBadgeCards`).
- [ ] Update `frontend/app/page.jsx` untuk menampilkan:
  - Sentiment timeline/barchart
  - Top headline highlight
  - Volatility/range metrics

### Testing manual
- [ ] Jalankan backend + frontend, analisa beberapa ticker (AAPL/BBCA) dan pastikan chart tidak error saat data parsial.
- [ ] Validasi format payload: chart menampilkan mapped_score per headline.

