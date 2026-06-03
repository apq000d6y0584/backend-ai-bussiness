# TODO - Fitur Kualitas Data & Keandalan

## Build/Deploy reliability
- Railway build fix (mise python@3.11.9 attestation verification failure)

### Checklist langkah
1. [x] Tambah `mise.toml` di root untuk menonaktifkan `python.github_attestations` agar `mise install` tidak gagal saat deploy.
2. [ ] Trigger ulang build/deploy Railway dan pastikan langkah `mise install python@3.11.9` sukses.

## Implementasi
 - Fallback CNBC yang lebih rapi: jika scraping CNBC gagal → jelaskan “menggunakan data terakhir / data parsial”.
 - Indikator status data: loading state per komponen (price ready / news ready / sentiment ready).
 - Retry + backoff untuk error sementara (network/rate limit).

## Checklist langkah (kualitas data)
1. [ ] Tambah retry + exponential backoff + status kualitas/fallback cache untuk scraping CNBC di `bi_engine.py`.
2. [ ] Ubah `BIEngine` agar tetap bisa menghasilkan analisis parsial saat news gagal (tetap kirim metadata kualitas per komponen).
3. [ ] Tambah endpoint usage di `api_server.py` bila perlu agar komponen bisa di-fetch terpisah.
4. [ ] Update frontend: ubah `frontend/lib/api.js` untuk mendukung fetch per komponen (stock/news/sentiment) + retry UI-level ringan.
5. [ ] Update frontend `frontend/app/page.jsx` agar memanggil price/news/sentiment secara paralel dan menyetel loading state per komponen.
6. [ ] Update `TransparencyExplainability.jsx` untuk mempertegas pesan “data terakhir / data parsial” sesuai metadata fallback.
7. [ ] Update komponen lain yang perlu (NewsList/PriceChart/SentimentBadge/ErrorState) agar menampilkan state parsial dengan baik.
8. [ ] Jalankan test manual:
   - CNBC gagal (simulasi dengan mematikan internet atau rate limit) → pastikan UI menampilkan parsial.
   - Case normal → semua komponen ready.

