# Business Intelligence API

REST API Server untuk analisis pasar dan sentiment menggunakan FastAPI, yfinance, dan BeautifulSoup.

## Deskripsi Project

Business Intelligence Engine adalah sistem analisis pasar yang menggabungkan:
- Data harga penutupan saham dari Yahoo Finance
- Berita terbaru dari CNBC World Markets
- Analisis sentimen otomatis
- Rekomendasi bisnis berbasis data

## Fitur

1. **Analisis Saham** - Ambil data harga penutupan 7 hari terakhir
2. **Scraping Berita** - Ambil judul berita terbaru dari CNBC
3. **Analisis Sentimen** - Skor sentimen 1-10 berbasis data kuantitatif dan kualitatif
4. **Rekomendasi Bisnis** - 3 rekomendasi berbasis analisis
5. **Caching** - Penyimpanan sementara untuk menghindari pemblokiran
6. **REST API** - Endpoint fleksibel untuk frontend Next.js

## Prasyarat

- Python 3.11 atau lebih baru
- pip (package installer)

## Instalasi

### 1. Clone atau download project ini

### 2. Buat virtual environment (disarankan)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Cara Menjalankan Server

### Jalankan API Server

```bash
python api_server.py
```

 atau

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Server akan berjalan di `http://localhost:8000`

## Mengakses di Browser Komputer Lokal

Setelah server berjalan, buka browser dan akses:

| Endpoint | URL | Deskripsi |
|----------|-----|-----------|
| Root | `http://localhost:8000` | Info dasar API |
| Health Check | `http://localhost:8000/health` | Status kesehatan server |
| Analisis Lengkap | `http://localhost:8000/api/bi?ticker=AAPL` | Analisis lengkap untuk ticker |
| Data Saham | `http://localhost:8000/api/stock?ticker=AAPL&days=7` | Data harga saham |
| Berita | `http://localhost:8000/api/news` | Berita terbaru |
| Sentimen | `http://localhost:8000/api/sentiment?ticker=AAPL` | Skor sentimen |
| Rekomendasi | `http://localhost:8000/api/recommendations?ticker=AAPL` | Strategi rekomendasi |
| API Docs | `http://localhost:8000/docs` | Dokumentasi interaktif (Swagger UI) |
| API Docs Alt | `http://localhost:8000/redoc` | Dokumentasi alternatif (ReDoc) |

## Contoh Penggunaan

### 1. Analisis Lengkap (Main Endpoint)

Buka di browser:
```
http://localhost:8000/api/bi?ticker=AAPL
```

Response contoh:
```json
{
  "status": "success",
  "ticker": "AAPL",
  "generated_at": "2024-01-15T10:30:00",
  "data": {
    "stock_data": {...},
    "news_data": {...},
    "sentiment": {"score": 7, "label": "Positif"},
    "recommendations": [...]
  }
}
```

### 2. Analisis Ticker Lain

Ganti `AAPL` dengan ticker lain:
- `MSFT` - Microsoft
- `GOOGL` - Google/Alphabet
- `TSLA` - Tesla
- `AMZN` - Amazon

Contoh:
```
http://localhost:8000/api/bi?ticker=MSFT
http://localhost:8000/api/bi?ticker=TSLA
```

### 3. Lihat Dokumentasi API Interaktif

Buka `http://localhost:8000/docs` untuk melihat semua endpoint dan mencoba langsung dari browser.

## Troubleshooting

### 1. Port 8000 sudah digunakan

Ganti port:
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8001
```

### 2. Error "No module named 'fastapi'"

Pastikan dependencies terinstall:
```bash
pip install -r requirements.txt
```

### 3. Data tidak muncul

Kemungkinan koneksi internet bermasalah. Cek koneksi dan coba lagi.

### 4. Cache error

Hapus folder cache secara manual:
```bash
rmdir /s /q cache
```

## environment_details

- **Python Version**: 3.11.9
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Port Default**: 8000

## Lisensi

MIT License
