# TODO_UX — User Experience (Wajib)

## Backend
- [ ] Tambahkan penyimpanan history per ticker (tanggal/jam, skor sentimen, ringkasan, top drivers, rekomendasi).
- [ ] Tambahkan REST API:
  - [ ] GET /api/history?ticker=...
  - [ ] POST/implicit save saat analisis selesai (atau saat endpoint /api/bi dipanggil)
- [ ] Tambahkan Watchlist/Favorites:
  - [ ] POST/PUT /api/watchlist (set daftar ticker)
  - [ ] GET /api/watchlist
  - [ ] DELETE /api/watchlist/:ticker
- [ ] Tambahkan Export:
  - [ ] GET /api/export?format=json&... (laporan per ticker)
  - [ ] GET /api/export?format=csv&... (laporan ringkas per ticker)
- [ ] Implement storage strategy:
  - [ ] Supabase jika env SUPABASE_URL/KEY & tabel tersedia
  - [ ] Fallback file JSON lokal jika Supabase tidak tersedia

## Frontend
- [ ] Deep link / share: read/write query param `ticker`.
- [ ] Watchlist panel UI:
  - [ ] Simpan daftar ticker
  - [ ] Tampilkan snapshot terbaru
  - [ ] Tombol Analyze dan "Lihat history"
- [ ] History UI:
  - [ ] Tampilkan list riwayat analisis per ticker
  - [ ] Tombol "lihat lagi" -> modal/drawer detail
- [ ] Auto-refresh terkontrol watchlist:
  - [ ] refresh periodik
  - [ ] indikator "Sedang update" per ticker
  - [ ] throttle/concurrency limit
- [ ] Export buttons:
  - [ ] Unduh JSON/CSV untuk ticker aktif (dan/atau dari history)

## Testing
- [ ] Jalankan backend + frontend
- [ ] Uji flow:
  - [ ] buka /?ticker=AAPL
  - [ ] tambah ke watchlist
  - [ ] tunggu auto-refresh
  - [ ] buka history & tekan "lihat lagi"
  - [ ] export JSON/CSV

