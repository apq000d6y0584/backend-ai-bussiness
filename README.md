
# Business Intelligence API & Frontend Dashboard

REST API Server + Next.js Frontend untuk analisis pasar dan sentiment menggunakan FastAPI + AI (FinBERT).

## 🚀 Quick Start

### 1. Backend (API Server)
```bash
pip install -r requirements.txt
python api_server.py
```
API berjalan di `http://localhost:8000`

### 2. Frontend (Dashboard)
```bash
cd frontend
npm install
npm run dev
```
Dashboard berjalan di `http://localhost:3000`

## 📱 Cara Penggunaan

1. Jalankan backend API (`python api_server.py`)
2. Jalankan frontend (`cd frontend && npm run dev`)
3. Buka `http://localhost:3000`
4. Masukkan ticker saham (AAPL, MSFT, TSLA, dll)
5. Lihat hasil analisis lengkap dengan grafik, sentiment, berita, dan rekomendasi!

## 🏗️ Arsitektur Jaringan (Production)

Proyek ini telah dikonfigurasi menggunakan arsitektur jaringan industri untuk mengatasi masalah *Mixed Content* pada Vercel dengan mengamankan lalu lintas data menggunakan HTTPS penuh:

*   **[ Cloud Hosting Frontend ]** (Vercel, Netlify, dll. - HTTPS)
    
    ⬇️ *(HTTPS Api Call)*
    
*   **[ Cloudflare Proxy ]** (SSL Full Mode)
    
    ⬇️ *(Reverse Proxy via Port 443 / SSL)*
    
*   **[ Alibaba Cloud ECS ]** (Nginx Web Server)
    
    ⬇️ *(Internal Routing to Port 8000)*
    
*   **[ FastAPI Backend ]** (Localhost HTTP)

## 🛠️ Fitur Sistem

### Backend API (Port 8000 / Production Subdomain)

| Endpoint | Deskripsi |
|----------|-----------|
| `/api/bi?ticker=AAPL` | **Analisis Lengkap** - Stock + News + Sentimen + Recommendations |
| `/api/stock?ticker=AAPL` | Data harga saham 7 hari |
| `/api/news` | Berita CNBC World Markets |
| `/api/sentiment?ticker=AAPL` | Skor sentimen FinBERT (1-10) |
| `/api/ihsg-dashboard` | **IHSG Market Dashboard** - Analisis heuristik tren harga saham Indonesia (Kategori: *Growth*, *Value*, *Value Trap*, *Zombie*, *Multibagger*, dan *Bagholder* proxy) |
| `/docs` | **Swagger UI** - Dokumentasi interaktif |

### Frontend Dashboard (Port 3000 / Live Deployment)
- ✅ Search bar untuk ticker saham eksternal
- ✅ **Stock Chart** (Recharts - 7 hari closing prices)
- ✅ **Sentiment Card** (FinBERT score 1-10 + progress bar)
- ✅ **News Feed** (CNBC headlines scraping)
- ✅ **Recommendations** (3 skala prioritas: tinggi/sedang/rendah)
- ✅ Akselerasi UI (Loading states + Error handling yang aman)
- ✅ Responsive design (Mobile-first menggunakan Tailwind CSS)

## 🔧 Environment Variables

### Backend (`.env`)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### Frontend (`.env.local` / Cloud Hosting Environment)
```env
# Jalur API Live yang sudah aman menggunakan HTTPS Subdomain
NEXT_PUBLIC_API_URL=https://bi-api.bonodigital.biz.id
```

## 🌐 Panduan Produksi & Deployment

Proyek ini dirancang dengan fleksibilitas tinggi dan dapat di-deploy menggunakan dua pendekatan arsitektur yang berbeda, sesuai dengan kebutuhan skala lingkungan kerja Anda:

### ⚡ Opsi 1: Cloud PaaS (Railway / Render / Heroku) - *Untuk Evaluasi Cepat*
Jika Anda melakukan *cloning* proyek ini untuk kebutuhan pengujian cepat atau lingkungan *staging*, Anda dapat menggunakan layanan PaaS instan:
1. Hubungkan repositori hasil *clone* Anda ke panel **Railway**, **Render**, atau **Heroku**.
2. Konfigurasikan Environment Variables berikut di panel penyedia layanan:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Tentukan perintah start server: `uvicorn api_server:app --host 0.0.0.0 --port 8000`.
4. Jalankan Deployment.

---

### 🏛️ Opsi 2: Production-Grade Infrastructure (Alibaba Cloud ECS + Cloudflare) - *Arsitektur Utama & Rekomendasi*
> **⚠️ Catatan Penting untuk Penilaian Capstone:**
> Untuk lingkungan *Live Production* resmi, kami **tidak menggunakan** layanan instan (PaaS). Proyek ini sepenuhnya diarsiteki menggunakan **Alibaba Cloud ECS (IaaS)** yang dikombinasikan dengan **Cloudflare Proxy**. 
>
> Pemilihan infrastruktur mandiri ini sengaja dilakukan sebagai bukti keseriusan tim dalam membangun sistem yang matang (*enterprise-ready*), memiliki kontrol penuh atas performa server, efisiensi biaya komputasi AI (FinBERT), serta implementasi proteksi jaringan berlapis (SSL Handshake Full Mode + Isolasi Port Internal via Nginx Reverse Proxy).

#### 1. Frontend (Vercel, Netlify, atau sejenisnya)
1. Hubungkan repositori GitHub ke panel platform cloud hosting Anda (misal: **Vercel** atau **Netlify**).
2. Masukkan `NEXT_PUBLIC_API_URL` dengan nilai `https://bi-api.bonodigital.biz.id`.
3. Klik **Deploy**.

#### 2. Backend Otomatis (Alibaba Cloud ECS via Script)
Untuk mempermudah proses pembaruan dan instalasi di server produksi (ECS), proyek ini telah dilengkapi dengan skrip otomatisasi deployment `deploy_ecs.sh`. Skrip ini secara otomatis akan memperbarui dependensi sistem, mengisolasi *Virtual Environment*, mengonfigurasi ulang Systemd Service `bi-engine`, dan memicu *restart* server secara aman.

**Langkah Eksekusi di Server ECS:**
1. Masuk ke server ECS Anda via SSH.
2. Masuk ke direktori proyek yang telah di-cloning:
   ```bash
   cd backend-ai-bussiness
   ```
3. Berikan izin akses eksekusi pada file skrip:
   ```bash
   chmod +x deploy_ecs.sh
   ```
4. Jalankan skrip deployment otomatis:
   ```bash
   ./deploy_ecs.sh
   ```

#### 3. Konfigurasi Manual Jaringan & Gateway (Nginx & Cloudflare)
Setelah skrip backend di atas berhasil dijalankan (Backend aktif di port internal `8000`), pastikan jalur pipa jaringan luar sudah dikonfigurasi sebagai berikut:

**A. Sinkronisasi Gateway Nginx:**
1. Salin file konfigurasi produksi dari repositori ke direktori sistem Nginx:
   ```bash
   sudo cp deployment/nginx.conf /etc/nginx/sites-available/bi-api
   ```
2. Aktifkan konfigurasi tautan (*symbolic link*):
   ```bash
   sudo ln -s /etc/nginx/sites-available/bi-api /etc/nginx/sites-enabled/
   ```
3. Uji konfigurasi Nginx lalu restart layanan:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

**B. Pengaturan Firewall & DNS:**
- **Cloudflare**: DNS Terarah menggunakan *A Record* `bi-api` terproksi awan jingga (*Proxied*) dengan enkripsi SSL bertipe **Full**.
- **Alibaba Cloud Security Group**: Membuka Port `80` (HTTP) dan `443` (HTTPS) untuk umum (`0.0.0.0/0`). Port internal `8000` otomatis terisolasi dengan aman dari publik karena dialihkan lewat internal routing Nginx.
- **Firewall Internal (OS)**: Status `ufw` dinonaktifkan (`inactive`) agar tidak tumpang tindih dengan kebijakan kelompok keamanan Alibaba Cloud.

## 📊 API Response Structure

```json
{
  "status": "success",
  "ticker": "AAPL",
  "data": {
    "stock_data": { "closing_prices": [170.5, 172.3], "price_change_percent": 2.5 },
    "news_data": { "headlines": ["News title 1", ...] },
    "sentiment": { "score": 7.2, "label": "Positif" },
    "recommendations": [
      { "title": "Buy", "description": "...", "priority": "tinggi" }
    ]
  }
}
```

## 🔧 Troubleshooting Produksi

| Gejala Masalah | Kode Error | Solusi |
|-------|----------|----------|
| Mixed Content di Vercel | Blocked By Browser | Pastikan pemanggilan API menggunakan URL HTTPS Subdomain resmi. |
| Cloudflare Connection Timeout | Error 522 | Periksa *Security Group* Alibaba Cloud, pastikan Port 80/443 diizinkan (`Allow`). |
| Web Server Is Down | Error 521 | Nginx belum diaktifkan di ECS atau belum dikonfigurasi mendengarkan port 443 SSL. |
| Analisis Melambat | Response Delay | Wajar terjadi pada pemanggilan awal (~10-30s) untuk proses memuat model FinBERT pertama kali. |

## 🧰 Tech Stack & Prasyarat

- **Spesifikasi minimum**: Python 3.11+, Node.js 18+ (NPM)
- **Backend**: FastAPI, yfinance, BeautifulSoup4, Transformers (FinBERT / DistilRoBERTa)
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, Axios
- **Database**: Supabase (Auto-save analisis pasar)

## Lisensi
MIT License
