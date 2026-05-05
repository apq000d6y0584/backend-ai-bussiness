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

## 🏗️ Arsitektur

```
Frontend (Next.js + Tailwind + Recharts) 
    ↕️ API Calls (axios)
Backend (FastAPI)
    ↕️ yfinance + CNBC scraping + FinBERT (HuggingFace)
Database (Supabase - optional)
```

## Fitur

### Backend API (Port 8000)
| Endpoint | Deskripsi |
|----------|-----------|
| `/api/bi?ticker=AAPL` | **Analisis Lengkap** - Stock + News + Sentiment + Recommendations |
| `/api/stock?ticker=AAPL` | Data harga saham 7 hari |
| `/api/news` | Berita CNBC World Markets |
| `/api/sentiment?ticker=AAPL` | Skor sentiment FinBERT (1-10) |
| `/docs` | **Swagger UI** - Dokumentasi interaktif |

### Frontend Dashboard (Port 3000)
- ✅ Search bar untuk ticker
- ✅ **Stock Chart** (Recharts - 7 hari closing prices)
- ✅ **Sentiment Card** (FinBERT score 1-10 + progress bar)
- ✅ **News Feed** (CNBC headlines)
- ✅ **Recommendations** (3 prioritas: tinggi/sedang/rendah)
- ✅ Loading states + Error handling
- ✅ Responsive design (mobile-first)
- ✅ Tailwind CSS styling

## 🛠️ Development

### Backend
```bash
# Install deps
pip install -r requirements.txt

# Run server
python api_server.py

# API Docs
http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
npm run build  # Production build
```

### Environment Variables
**Backend (.env)**
```
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Deployment

### Backend (Railway/Render/Heroku)
1. Push ke GitHub
2. Connect ke Railway/Render
3. Set env vars `SUPABASE_URL` + `SUPABASE_KEY`
4. Deploy!

### Frontend (Vercel)
1. Push ke GitHub
2. Connect ke Vercel
3. Set `NEXT_PUBLIC_API_URL` ke URL backend live
4. Deploy!

**CORS Note**: Backend sudah allow all origins (`*`). Update untuk production.

## 📊 API Response Structure

```json
{
  "status": "success",
  "ticker": "AAPL",
  "data": {
    "stock_data": { "closing_prices": [...], "price_change_percent": 2.5 },
    "news_data": { "headlines": ["News title 1", ...] },
    "sentiment": { "score": 7.2, "label": "Positif" },
    "recommendations": [
      { "title": "Buy", "description": "...", "priority": "tinggi" }
    ]
  }
}
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `npm install` fails | Delete `node_modules` + `package-lock.json`, retry |
| TypeScript errors | `npm install` deps sudah lengkap |
| Backend 500 | Check logs, pastikan internet untuk yfinance/CNBC |
| CORS error | Backend CORS sudah `*`, update untuk prod |
| Slow analysis | Normal (FinBERT ~10-30s pertama kali) |

## Prasyarat

```
Backend: Python 3.11+, pip
Frontend: Node.js 18+, npm
```

## Tech Stack

- **Backend**: FastAPI, yfinance, BeautifulSoup, transformers (FinBERT)
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, axios
- **AI**: DistilRoBERTa (financial sentiment)
- **DB**: Supabase (optional, auto-save)

## Lisensi
MIT License

---
*Built with ❤️ using BLACKBOXAI*

