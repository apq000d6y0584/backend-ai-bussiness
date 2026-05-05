# Abstrak Analisis Kode BI-AI Engine

## Ringkasan Arsitektur Sistem

**BI-AI Engine** adalah sistem analisis **Business Intelligence** yang mengintegrasikan data **kuantitatif** (harga saham) dan **kualitatif** (berita pasar) untuk menghasilkan **skor sentimen** (1-10) dan **rekomendasi bisnis** otomatis. Sistem ini diimplementasikan dengan **Python** menggunakan **FastAPI** sebagai REST API server, dengan **Supabase** sebagai database backend.

## Komponen Utama (Modular Design)

### 1. **bi_engine.py** (Core Business Logic - 800+ lines)
```
Data Flow: yfinance → CNBC Scraping → FinBERT → Recommendations
```
- **StockDataCollector**: Mengambil harga penutupan 7 hari dari **Yahoo Finance** (yfinance)
- **NewsScraper**: Web scraping **CNBC World Markets** dengan **BeautifulSoup** + filtering keyword bisnis
- **DLAnalyzer** (Singleton): **FinBERT/DistilRoBERTa** untuk analisis sentimen berita (skor 1-10)
- **MarketAnalyzer**: Menggabungkan data kuantitatif + kualitatif
- **SentimentScorer**: Skor gabungan (40% harga + 60% sentimen)
- **BusinessRecommender**: Generate 3 rekomendasi bisnis
- **BIEngine**: Orchestrator utama dengan **proxy fix** untuk Supabase

### 2. **api_server.py** (FastAPI REST API)
```
Endpoints: /api/bi?ticker=AAPL → JSON Response untuk Next.js
```
- **7+ endpoints** (`/api/bi`, `/stock`, `/news`, `/sentiment`, `/batch`, `/graphql`, `/cache`)
- **Pydantic validation** untuk input/output
- **CORS middleware** untuk frontend integration
- **WebSocket support** (real-time)
- **Swagger UI** (`/docs`) untuk testing

### 3. **supabase_handler.py** (Database Layer)
```
Supabase Integration dengan proxy workaround
```
- **Lazy client initialization**
- **Upsert strategy** untuk menghindari data duplication
- **5 table operations**: `stock_data`, `news_data`, `analysis`, `sentiment_score`, `recommendations`

### 4. **Caching System**
```
File-based cache (cache/*.json) + 1-hour TTL
```
- **CacheManager**: MD5 hash key + timestamp validation
- **clear_cache()** endpoint

## Teknologi Stack

```
Backend: FastAPI + Uvicorn
ML: Transformers (FinBERT/DistilRoBERTa) + Torch
Data: yfinance + BeautifulSoup + Supabase
Validation: Pydantic
Deployment: Railway/Heroku ready (Procfile)
```

## Data Processing Pipeline

```
1. Input: ticker (AAPL/MSFT)
2. ↓ StockDataCollector (yfinance)
3. ↓ NewsScraper (CNBC scraping)
4. ↓ DLAnalyzer.FinBERT (sentimen berita)
5. ↓ MarketAnalyzer (gabung data)
6. ↓ SentimentScorer (skor 1-10)
7. ↓ BusinessRecommender (3 insight)
8. ↓ Supabase (persist)
9. ↓ JSON Response
```

## Fitur Kunci

| Fitur | Deskripsi | Teknologi |
|-------|-----------|-----------|
| **Sentimen AI** | FinBERT analisis 10+ berita CNBC | DistilRoBERTa |
| **Real-time Data** | Harga live + berita terkini | yfinance + Scraping |
| **Caching** | Hindari rate limiting | File-based + TTL |
| **API Ready** | Swagger + CORS | FastAPI |
| **Database** | Auto-save analysis | Supabase PostgreSQL |
| **Batch Analysis** | Multiple ticker | GraphQL-style |

## Deployment Ready

```
Procfile: web: uvicorn api_server:app
runtime.txt: python-3.11.9
Environment: SUPABASE_URL + SUPABASE_KEY
```

## **Strengths**
✅ **Production-ready** dengan error handling + logging  
✅ **Modular architecture** (SRP diikuti)  
✅ **AI-powered** (FinBERT state-of-the-art)  
✅ **Scalable** (FastAPI async + caching)  
✅ **Frontend friendly** (JSON + CORS)  

## **Areas for Improvement**
🔄 **Supabase proxy fix** bisa di-refactor  
🔄 **News sources** tambah diversifikasi (Reuters, Bloomberg)  
🔄 **Monitoring** (Prometheus/Grafana)  

**Kesimpulan**: Sistem **lengkap dan robust** untuk analisis pasar real-time dengan **AI sentimen analysis**. Siap production dengan **1 command deployment**.
