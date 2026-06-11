# Perbaikan error: `Failed to analyze NEXT_PUBLIC_API_URL is not defined`

## Penyebab
Kode mengambil backend base URL dari environment variable berikut:

- `process.env.NEXT_PUBLIC_API_URL`

Jika variabel itu kosong/tidak ada, fungsi akan melempar:
- `throw new Error('NEXT_PUBLIC_API_URL is not defined')`

Variabel ini dipakai untuk membentuk:
- REST endpoint: `.../api/bi`
- WebSocket endpoint: `.../ws`

## Solusi (lokal)
1. Pastikan ada file:
   - `frontend/.env.local`
   (bukan hanya `frontend/.env.local.example`)
2. Isi contoh berikut (sesuaikan host/port backend kamu):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Restart server Next.js.

> Catatan: `NEXT_PUBLIC_*` harus tersedia saat build/runtime Next.

## Solusi (deploy: Netlify)
Jika aplikasi dideploy, buat environment variable di Netlify:
- Key: `NEXT_PUBLIC_API_URL`
- Value: `http(s)://host-backend:port`

Lalu redeploy.

## Verifikasi cepat
- Kalau sudah benar, tidak akan muncul error `NEXT_PUBLIC_API_URL is not defined` lagi.
- Request REST dan WebSocket akan memakai base URL yang sama.

