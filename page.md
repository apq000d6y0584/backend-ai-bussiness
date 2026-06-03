# Halaman Frontend (Next.js)

Frontend ini adalah dashboard berbasis **Next.js (App Router)** untuk menampilkan **stock sentiment** dan **rekomendasi**.

## Struktur penting
- `frontend/app/page.tsx` : Halaman utama dashboard (UI semua komponen).
- `frontend/app/components/` : Komponen-komponen UI:
  - `SearchBar` : input ticker & tombol Analyze
  - `LoadingSkeleton` : skeleton saat loading
  - `ErrorState` : tampilan error
  - `MetricCards` : current price, price change, sentiment score
  - `PriceChart` : chart trend 7 hari
  - `NewsList` : daftar headline berita
  - `RecommendationsList` : daftar rekomendasi

## Endpoint/halaman yang bisa dikunjungi
- Dashboard utama:
  - **http://localhost:3000/**

(halaman ini render dari file `frontend/app/page.tsx`, karena Next App Router memetakan `app/page.tsx` ke `/`)

## Cara menjalankan
1. Masuk ke folder frontend:
   - `cd frontend`
2. Install dependency:
   - `npm install`
3. Jalankan dev server:
   - `npm run dev`
4. Buka browser:
   - `http://localhost:3000/`

## Catatan integrasi JSON
UI membaca response JSON dari backend dan menampilkan:
- data saham (chart & metric)
- daftar headline berita
- rekomendasi

