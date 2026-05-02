"""
Business Intelligence Engine - Market Analysis System
Menggunakan yfinance dan BeautifulSoup untuk analisis pasar

Fitur:
1. Ambil data harga penutupan 7 hari terakhir
2. Scrape judul berita dari CNBC World Markets
3. Gabungkan data kuantitatif dan kualitatif
4. Analisis performa pasar dengan sentiment analysis
5. Skor sentimen (1-10)
6. 3 Rekomendasi bisnis
"""

# ========== CRITICAL: Remove proxy vars at module load time ==========
# Supabase client doesn't support proxy - must clear BEFORE import
# This MUST be the very first thing done
import os as _sys_os
_proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
for _pv in _proxy_vars:
    if _pv in _sys_os.environ:
        del _sys_os.environ[_pv]

# Clear any custom proxy env vars that might exist
if 'SUPABASE_PROXY' in _sys_os.environ:
    del _sys_os.environ['SUPABASE_PROXY']
if 'DATABASE_PROXY' in _sys_os.environ:
    del _sys_os.environ['DATABASE_PROXY']

# Clean up module-level variables
del _sys_os, _proxy_vars, _pv
# ========== End proxy fix ==========

import json
import re
import time
import hashlib
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

import requests
import yfinance
from bs4 import BeautifulSoup
import numpy as np

# ========== PROXY FIX: Import supabase with error handling ==========
# Import after proxy vars are cleared from environment
try:
    from supabase import create_client, Client
except TypeError as _e:
    # Handle proxy-related import errors
    if "proxy" in str(_e).lower():
        import sys
        # Force reimport without proxy-related cached modules
        _mods_to_remove = [k for k in sys.modules if 'supabase' in k or 'http' in k]
        for _m in _mods_to_remove:
            sys.modules.pop(_m, None)
        from supabase import create_client, Client
    else:
        raise
# ========== End supabase import fix ==========

# Transformers for FinBERT sentiment analysis
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== DL ANALYZER (FinBERT) - Singleton Pattern ====================
class DLAnalyzer:
    """
    Deep Learning Analyzer menggunakan FinBERT untuk analisis sentimen.
    Menggunakan Singleton pattern agar model hanya di-load sekali.
    """
    _instance = None
    _model = None
    _tokenizer = None
    _sentiment_pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DLAnalyzer, cls).__new__(cls)
        return cls._instance

    def _load_model(self):
        """
        Load DistilRoBERTa yang lebih ringan (lazy loading).
        Cocok untuk lingkungan dengan RAM terbatas seperti Railway.
        """
        if self._sentiment_pipeline is None:
            try:
                # Menggunakan model DistilRoBERTa khusus finansial
                model_name = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
                logger.info(f"Menginisialisasi model ringan: {model_name}...")
                
                self._sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=model_name,
                    tokenizer=model_name,
                    device=-1  # Menggunakan CPU untuk efisiensi memori
                )
                logger.info("DistilRoBERTa berhasil dimuat!")
            except Exception as e:
                logger.error(f"Gagal memuat model: {e}")
                raise

    def analyze_sentiment(self, headlines: List[str]) -> Dict[str, Any]:
        """
        Analisis sentimen untuk setiap headline menggunakan FinBERT.
        
        Args:
            headlines: List dari judul berita
            
        Returns:
            Dictionary dengan hasil analisis sentimen per headline dan rata-rata
        """
        # Lazy load model saat pertama kali digunakan
        self._load_model()

        if not headlines:
            return {
                "success": True,
                "headlines_analyzed": 0,
                "average_score": 5.0,
                "average_label": "Netral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "results": []
            }

        results = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for headline in headlines:
            try:
                # Batasi panjang teks untuk FinBERT (max 512 tokens)
                text = headline[:512] if len(headline) > 512 else headline
                
                # Analisis sentimen
                output = self._sentiment_pipeline(text)[0]
                
                # FinBERT output: positive, negative, neutral
                # Konversi ke skor 1-10
                label = output['label'].lower()
                score = output['score']

                # Map ke skor 1-10
                if label == 'positive':
                    mapped_score = round(5 + (score * 5))  # 5-10
                    mapped_score = min(10, max(6, mapped_score))
                    positive_count += 1
                elif label == 'negative':
                    mapped_score = round(5 - (score * 5))  # 1-5
                    mapped_score = min(5, max(1, mapped_score))
                    negative_count += 1
                else:  # neutral
                    mapped_score = 5
                    neutral_count += 1

                results.append({
                    "headline": headline,
                    "finbert_label": output['label'],
                    "finbert_score": round(score, 4),
                    "mapped_score": mapped_score
                })

            except Exception as e:
                logger.warning(f"Error analyzing headline: {e}")
                results.append({
                    "headline": headline,
                    "finbert_label": "neutral",
                    "finbert_score": 0.5,
                    "mapped_score": 5
                })
                neutral_count += 1

        # Hitung rata-rata skor
        total = len(results)
        if total > 0:
            avg_score = sum(r['mapped_score'] for r in results) / total
            avg_score = round(avg_score, 1)
        else:
            avg_score = 5.0

        # Tentukan label rata-rata
        if avg_score >= 7:
            avg_label = "Positif"
        elif avg_score >= 5:
            avg_label = "Netral"
        else:
            avg_label = "Negatif"

        return {
            "success": True,
            "headlines_analyzed": total,
            "average_score": avg_score,
            "average_label": avg_label,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "results": results
        }

    def get_average_sentiment(self, headlines: List[str]) -> Dict[str, Any]:
        """
        fungsi merata-ratakan skor sentimen dari semua berita menjadi skala 1-10.
        
        Args:
            headlines: List dari judul berita
            
        Returns:
            Dictionary dengan skor rata-rata dan breakdown
        """
        result = self.analyze_sentiment(headlines)
        
        return {
            "score": result.get("average_score", 5.0),
            "label": result.get("average_label", "Netral"),
            "breakdown": {
                "positive_count": result.get("positive_count", 0),
                "negative_count": result.get("negative_count", 0),
                "neutral_count": result.get("neutral_count", 0),
                "total_headlines": result.get("headlines_analyzed", 0)
            }
        }

# ==================== CONFIGURATION ====================
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

CACHE_DURATION = 3600  # 1 jam dalam detik

# Kata kunci untuk filter berita yang relevan dengan fundamental bisnis
BUSINESS_KEYWORDS = [
    "stock", "market", "trade", "economy", "economic", "finance",
    "investment", "investor", "share", "shares", "dividend", "profit",
    "revenue", "earnings", "growth", "quarter", "fiscal", "CEO",
    "company", "business", "merger", "acquisition", "bull", "bear",
    "index", "nasdaq", "dow", "spy", "federal", "reserve", "inflation",
    "interest", "rate", "gdp", "consumer", "price", "outlook", "forecast"
]

# Kata kunci untuk analisis sentimen
POSITIVE_KEYWORDS = [
    "gain", "rise", "surge", "soar", "jump", "grow", "growth",
    "profit", "beat", "exceed", "bullish", "upgrade", "buy",
    "outperform", "positive", "strong", "improve", "recovery",
    "rally", "boost", "success", "achieve", "record", "high"
]

NEGATIVE_KEYWORDS = [
    "fall", "drop", "decline", "loss", "lose", "bearish", "downgrade",
    "sell", "underperform", "negative", "weak", "concern", "fear",
    "crash", "plunge", "sink", "recession", "risk", "warn",
    "miss", "fail", "trouble", "uncertain", "volatile"
]


class CacheManager:
    """Manajemen caching untuk menghindari pemblokiran"""

    @staticmethod
    def _get_cache_key(prefix: str, ticker: str = "") -> str:
        """Generate cache key berdasarkan prefix dan ticker"""
        raw = f"{prefix}:{ticker}:{datetime.now().date()}"
        return hashlib.md5(raw.encode()).hexdigest()

    @staticmethod
    def get(prefix: str, ticker: str = "") -> Optional[Dict]:
        """Ambil data dari cache jika masih valid"""
        cache_file = CACHE_DIR / f"{CacheManager._get_cache_key(prefix, ticker)}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)

            # Periksa apakah cache masih valid
            cache_time = cached.get("timestamp", 0)
            if time.time() - cache_time > CACHE_DURATION:
                cache_file.unlink()
                return None

            logger.info(f"Cache hit: {prefix} - {ticker}")
            return cached.get("data")

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Cache error: {e}")
            return None

    @staticmethod
    def set(prefix: str, ticker: str, data: Dict) -> None:
        """Simpan data ke cache"""
        cache_file = CACHE_DIR / f"{CacheManager._get_cache_key(prefix, ticker)}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": time.time(),
                    "data": data
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Cache saved: {prefix} - {ticker}")

        except IOError as e:
            logger.warning(f"Cache write error: {e}")

    @staticmethod
    def clear_cache() -> None:
        """Hapus cache untuk semua data (bukan berdasarkan prefix)"""
        try:
            for cache_file in CACHE_DIR.glob("*.json"):
                cache_file.unlink()
            logger.info("All cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")

    @staticmethod
    def clear_all() -> dict:
        """Hapus semua cache - alias untuk clear_cache"""
        CacheManager.clear_cache()
        return {"status": "success", "message": "Cache cleared"}

    @staticmethod
    def list_caches() -> List[dict]:
        """List semua cache yang tersedia"""
        caches = []
        try:
            for cache_file in CACHE_DIR.glob("*.json"):
                # Ekstrak prefix dan ticker dari nama file
                parts = cache_file.stem.split("_")
                if len(parts) >= 2:
                    caches.append({
                        "prefix": parts[0],
                        "ticker": parts[1] if len(parts) > 1 else "",
                        "file": cache_file.name
                    })
        except Exception as e:
            logger.warning(f"List cache error: {e}")
        return caches


class StockDataCollector:
    """Fungsi Pertama: Ambil data harga penutupan 7 hari terakhir"""

    @staticmethod
    def get_closing_prices(ticker: str, days: int = 7) -> Dict[str, Any]:
        """
        Ambil data harga penutupan untuk 7 hari terakhir

        Args:
            ticker: Simbol saham (contoh: 'AAPL', 'MSFT')
            days: Jumlah hari yang diambil

        Returns:
            Dictionary dengan harga penutupan dan metadata
        """
        cache_key = f"stock_{ticker}"

        # Cek cache terlebih dahulu
        cached_data = CacheManager.get("stock", ticker)
        if cached_data:
            return cached_data

        try:
            logger.info(f"Mengambil data saham untuk {ticker}")

            # Ambil data dari Yahoo Finance
            stock = yfinance.Ticker(ticker)

            # Ambil data historis untuk 7 hari terakhir + buffer untuk weekend
            hist = stock.history(period=f"{days + 5}d", interval="1d")

            if hist.empty:
                return {
                    "success": False,
                    "error": f"Tidak ada data untuk ticker {ticker}",
                    "ticker": ticker
                }

            # Ambil hari kerja (排除 weekend)
            closing_prices = []
            dates = []

            for idx, row in hist.iterrows():
                if len(closing_prices) >= days:
                    break
                # Skip jika harga closes = 0 (tidak ada trading)
                if row['Close'] > 0:
                    closing_prices.append(round(float(row['Close']), 2))
                    dates.append(idx.strftime("%Y-%m-%d"))

            # Hitung statistik
            if len(closing_prices) >= 2:
                price_change = closing_prices[-1] - closing_prices[0]
                price_change_pct = (price_change / closing_prices[0]) * 100
                avg_price = sum(closing_prices) / len(closing_prices)
            else:
                price_change = 0
                price_change_pct = 0
                avg_price = closing_prices[0] if closing_prices else 0

            result = {
                "success": True,
                "ticker": ticker,
                "data": {
                    "dates": dates,
                    "closing_prices": closing_prices,
                    "current_price": closing_prices[-1] if closing_prices else None,
                    "price_change": round(price_change, 2),
                    "price_change_percent": round(price_change_pct, 2),
                    "average_price": round(avg_price, 2),
                    "highest_price": max(closing_prices) if closing_prices else None,
                    "lowest_price": min(closing_prices) if closing_prices else None
                },
                "timestamp": datetime.now().isoformat()
            }

            # Simpan ke cache
            CacheManager.set("stock", ticker, result)

            return result

        except yfinance.exceptions.YFinanceException as e:
            logger.error(f"YFinance error: {e}")
            return {
                "success": False,
                "error": f"Yahoo Finance error: {str(e)}",
                "ticker": ticker
            }
        except Exception as e:
            logger.error(f"Error mengambil data saham: {e}")
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "ticker": ticker
            }


class NewsScraper:
    """Fungsi Kedua: Scrape judul berita dari CNBC World Markets"""

    BASE_URL = "https://www.cnbc.com/investing/"

    # Header untuk simulasi browser
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    @staticmethod
    def _clean_html_tags(text: str) -> str:
        """Bersihkan teks dari tag HTML"""
        if not text:
            return ""

        # Hapus semua tag HTML
        clean = re.sub(r'<[^>]+>', '', text)
        # Hapus spasi berlebihan
        clean = re.sub(r'\s+', ' ', clean)
        # Hapus special characters
        clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', clean)

        return clean.strip()

    @staticmethod
    def _is_relevant_news(headline: str) -> bool:
        """Periksa apakah berita relevan dengan fundamental bisnis"""
        if not headline:
            return False

        headline_lower = headline.lower()

        # Hitung jumlah keyword bisnis yang muncul
        keyword_count = sum(
            1 for keyword in BUSINESS_KEYWORDS
            if keyword.lower() in headline_lower
        )

        # Berita relevan jika mengandung minimal 1 keyword bisnis
        return keyword_count >= 1

    @staticmethod
    def get_world_markets_news() -> Dict[str, Any]:
        """
        Scrape judul berita dari CNBC World Markets

        Returns:
            Dictionary dengan daftar judul berita yang sudah dibersihkan
        """
        # Cek cache terlebih dahulu
        cached_data = CacheManager.get("news", "world_markets")
        if cached_data:
            return cached_data

        try:
            logger.info("Mengambil berita dari CNBC World Markets")

            # Coba beberapa endpoint CNBC
            urls_to_try = [
                "https://www.cnbc.com/investing/",
                "https://www.cnbc.com/investing/markets/",
                "https://www.cnbc.com/investing/world-markets/"
            ]

            all_headlines = []

            for url in urls_to_try:
                try:
                    response = requests.get(
                        url,
                        headers=NewsScraper.HEADERS,
                        timeout=10
                    )

                    if response.status_code != 200:
                        continue

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Cari semua headline - berbagai selector yang mungkin
                    headline_elements = soup.find_all(
                        ['h2', 'h3', 'a'],
                        class_=re.compile(r'headline|title|MigrationText', re.I)
                    )

                    # Jika tidak ada, cari semua link yang，看起来 seperti berita
                    if not headline_elements:
                        headline_elements = soup.find_all('a')

                    for elem in headline_elements:
                        # Ambil text dari elemen atau sibling
                        headline = elem.get_text()
                        if not headline:
                            # Coba cari dalam elemen turunannya
                            title_elem = elem.find(['span', 'p', 'h2', 'h3'])
                            if title_elem:
                                headline = title_elem.get_text()

                        if headline:
                            cleaned = NewsScraper._clean_html_tags(headline)

                            # Filter: minimal 10 karakter, maksimal 200
                            if 10 <= len(cleaned) <= 200:
                                all_headlines.append(cleaned)

                    # Jika sudah dapat berita, berhenti
                    if all_headlines:
                        break

                except requests.RequestException as e:
                    logger.warning(f"Error fetching {url}: {e}")
                    continue

            # Filter berita yang relevan dengan fundamental bisnis
            relevant_headlines = [
                headline for headline in all_headlines
                if NewsScraper._is_relevant_news(headline)
            ]

            # Jika tidak ada berita relevan, tetap gunakan semua berita
            if not relevant_headlines:
                relevant_headlines = all_headlines[:10] if all_headlines else []

            # Batasi maksimal 10 berita
            relevant_headlines = relevant_headlines[:10]

            result = {
                "success": True,
                "source": "CNBC World Markets",
                "data": {
                    "headlines": relevant_headlines,
                    "total_found": len(all_headlines),
                    "relevant_count": len(relevant_headlines)
                },
                "timestamp": datetime.now().isoformat()
            }

            # Simpan ke cache
            CacheManager.set("news", "world_markets", result)

            return result

        except requests.RequestException as e:
            logger.error(f"Connection error: {e}")
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "source": "CNBC World Markets"
            }
        except Exception as e:
            logger.error(f"Error scraping news: {e}")
            return {
                "success": False,
                "error": f"Scraping error: {str(e)}",
                "source": "CNBC World Markets"
            }


class DataMerger:
    """Fungsi Ketiga: Gabungkan data kuantitatif dan kualitatif"""

    @staticmethod
    def merge_data(
        stock_data: Dict[str, Any],
        news_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gabungkan data harga saham dan berita menjadi satu dictionary

        Args:
            stock_data: Hasil dari StockDataCollector
            news_data: Hasil dari NewsScraper

        Returns:
            Dictionary yang menggabungkan kedua data
        """
        merged = {
            "success": stock_data.get("success", False) and news_data.get("success", False),
            "ticker": stock_data.get("ticker"),
            "quantitative_data": stock_data.get("data", {}),
            "qualitative_data": news_data.get("data", {}),
            "merged_at": datetime.now().isoformat()
        }

        # Jika salah satu gagal, tambahkan error
        if not merged["success"]:
            errors = []
            if not stock_data.get("success", False):
                errors.append(stock_data.get("error", "Stock data unavailable"))
            if not news_data.get("success", False):
                errors.append(news_data.get("error", "News data unavailable"))
            merged["errors"] = errors

        return merged


class MarketAnalyzer:
    """Fungsi Empat: Analisis performa pasar"""

    @staticmethod
    def analyze_performance(merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisis performa pasar berdasarkan data kuantitatif dan kualitatif

        Args:
            merged_data: Data yang sudah digabungkan

        Returns:
            Dictionary dengan analisis dan rekomendasi
        """
        stock_data = merged_data.get("quantitative_data", {})
        news_data = merged_data.get("qualitative_data", {})

        # Analisis kuantitatif - data harga
        price_change = stock_data.get("price_change_percent", 0)
        current_price = stock_data.get("current_price")

        # Analisis kuantitatif sederhana
        if price_change > 2:
            quantitative_trend = "positif"
            quantitative_signal = "买入"
        elif price_change < -2:
            quantitative_trend = "negatif"
            quantitative_signal = "卖出"
        else:
            quantitative_trend = "netral"
            quantitative_signal = "持有"

        # Analisis kualitatif - berita menggunakan FinBERT (DLAnalyzer)
        headlines = news_data.get("headlines", [])

        # Gunakan DLAnalyzer untuk analisis sentimen FinBERT
        dl_analyzer = DLAnalyzer()
        finbert_result = dl_analyzer.analyze_sentiment(headlines)

        positive_count = finbert_result.get("positive_count", 0)
        negative_count = finbert_result.get("negative_count", 0)
        neutral_count = finbert_result.get("neutral_count", 0)
        avg_finbert_score = finbert_result.get("average_score", 5.0)
        avg_finbert_label = finbert_result.get("average_label", "Netral")

        # Tentukan trend kualitatif dari FinBERT
        if avg_finbert_score >= 7:
            qualitative_trend = "positif"
        elif avg_finbert_score <= 4:
            qualitative_trend = "negatif"
        else:
            qualitative_trend = "netral"

        # Ringkasan eksekutif
        ticker = merged_data.get("ticker", "N/A")
        executive_summary = (
            f"Analisis pasar untuk {ticker}: "
            f"Dari sisi kuantitatif, harga menunjukkan tren {quantitative_trend} "
            f"dengan perubahan {price_change:.2f}% dalam 7 hari terakhir. "
            f"Dari sisi kualitatif (FinBERT), sentiment berita menunjukkan kecenderungan {qualitative_trend} "
            f"dengan skor rata-rata {avg_finbert_score}/10 ({positive_count} berita positif, {negative_count} negatif, {neutral_count} netral). "
        )

        # Analisis sentimen gabungan
        combined_sentiment = (avg_finbert_score / 10 + (0.5 if price_change >= 0 else 0.5)) / 2

        return {
            "executive_summary": executive_summary,
            "quantitative_analysis": {
                "trend": quantitative_trend,
                "signal": quantitative_signal,
                "price_change_percent": price_change,
                "current_price": current_price
            },
            "qualitative_analysis": {
                "trend": qualitative_trend,
                "finbert_average_score": avg_finbert_score,
                "finbert_average_label": avg_finbert_label,
                "positive_news_count": positive_count,
                "negative_news_count": negative_count,
                "neutral_news_count": neutral_count,
                "headlines_sample": headlines[:3],
                "finbert_results": finbert_result.get("results", [])[:5]  # Simpan 5 hasil teratas
            },
            "combined_analysis": {
                "quantitative_sentiment": quantitative_trend,
                "qualitative_sentiment": qualitative_trend
            }
        }


class SentimentScorer:
    """Fungsi Lima: Berikan skor sentimen (1-10)"""

    @staticmethod
    def calculate_sentiment_score(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hitung skor sentimen 1-10 menggunakan FinBERT (DLAnalyzer)

        Args:
            analysis_data: Hasil analisis dari MarketAnalyzer

        Returns:
            Dictionary dengan skor dan breakdown
        """
        # Skor kuantitatif (berdasarkan perubahan harga)
        price_change = analysis_data.get("quantitative_analysis", {}).get("price_change_percent", 0)

        if price_change >= 5:
            q_score = 10
        elif price_change >= 3:
            q_score = 8
        elif price_change >= 1:
            q_score = 7
        elif price_change >= -1:
            q_score = 5
        elif price_change >= -3:
            q_score = 3
        elif price_change >= -5:
            q_score = 2
        else:
            q_score = 1

        # Skor kualitatif dari FinBERT (sudah di-calculate di DLAnalyzer)
        finbert_avg_score = analysis_data.get("qualitative_analysis", {}).get("finbert_average_score", 5.0)
        
        # Konversi FinBERT score (1-10) ke k_score
        # FinBERT sudah return 1-10, langsung gunakan
        k_score = round(finbert_avg_score)

        # Skor gabungan (bobot: 40% kuantitatif, 60% kualitatif)
        final_score = round((q_score * 0.4) + (k_score * 0.6))

        # Tentukan label
        if final_score >= 9:
            label = "Sangat Positif"
        elif final_score >= 7:
            label = "Positif"
        elif final_score >= 5:
            label = "Netral"
        elif final_score >= 3:
            label = "Negatif"
        else:
            label = "Sangat Negatif"

        # Breakdown dari FinBERT
        finbert_breakdown = analysis_data.get("qualitative_analysis", {}).get("finbert_results", [])

        return {
            "score": final_score,
            "label": label,
            "breakdown": {
                "quantitative_score": q_score,
                "quantitative_weight": "40%",
                "finbert_score": finbert_avg_score,
                "qualitative_weight": "60%",
                "finbert_positive_count": analysis_data.get("qualitative_analysis", {}).get("positive_news_count", 0),
                "finbert_negative_count": analysis_data.get("qualitative_analysis", {}).get("negative_news_count", 0),
                "finbert_neutral_count": analysis_data.get("qualitative_analysis", {}).get("neutral_news_count", 0),
                "finbert_results_sample": finbert_breakdown[:3]
            },
            "interpretation": f"Skor {final_score}/10 menunjukkan sentiment {label.lower()}"
        }


class BusinessRecommender:
    """Fungsi Enam: Berikan 3 rekomendasi bisnis"""

    @staticmethod
    def generate_recommendations(
        analysis_data: Dict[str, Any],
        sentiment_score: int
    ) -> List[Dict[str, str]]:
        """
        Generate 3 rekomendasi bisnis berdasarkan data

        Args:
            analysis_data: Hasil analisis dari MarketAnalyzer
            sentiment_score: Skor sentimen

        Returns:
            List of 3 rekomendasi
        """
        recommendations = []

        q_trend = analysis_data.get("quantitative_analysis", {}).get("trend", "netral")
        k_trend = analysis_data.get("qualitative_analysis", {}).get("trend", "netral")
        price_change = analysis_data.get("quantitative_analysis", {}).get("price_change_percent", 0)

        # Rekomendasi 1:基于价格趋势
        if q_trend == "positif":
            recommendations.append({
                "title": "Pertimbangkan Posisi Long",
                "description": f"Harga naik {price_change:.2f}% dalam 7 hari. Tren positif, pertimbangkan posisi long dengan stop loss.",
                "priority": "tinggi"
            })
        elif q_trend == "negatif":
            recommendations.append({
                "title": "Tunda Keputusan Beli",
                "description": f"Harga turun {abs(price_change):.2f}% dalam 7 hari. Tunggu konfirmasi breakout sebelum membuka posisi.",
                "priority": "sedang"
            })
        else:
            recommendations.append({
                "title": "Pertahankan Posisi Saat Ini",
                "description": "Harga stabil. Pertahankan posisi dan tunggu signal yang lebih jelas.",
                "priority": "rendah"
            })

        # Rekomendasi 2:基于新闻 sentiment
        if sentiment_score >= 7:
            recommendations.append({
                "title": "Diversifikasi Portfolio",
                "description": "Sentiment berita positif. Saatnya mempertimbangkan diversifikasi ke sektor terkait.",
                "priority": "sedang"
            })
        elif sentiment_score <= 3:
            recommendations.append({
                "title": "Tingkatkan Kewaspadaan",
                "description": "Sentiment berita negatif. Tingkatkan monitoring dan pertimbangkan hedging.",
                "priority": "tinggi"
            })
        else:
            recommendations.append({
                "title": "Lakukan Review Berkala",
                "description": "Sentiment netral. Review portofolio secara berkala untuk peluang yang lebih jelas.",
                "priority": "rendah"
            })

        # Rekomendasi 3:基于综合分析
        if q_trend == k_trend:
            recommendations.append({
                "title": "Konfirmasi Signal",
                "description": f"Analisis kuantitatif dan kualitatif saling mengkonfirmasi ({q_trend}). Signal kuat untuk aksi.",
                "priority": "tinggi"
            })
        else:
            recommendations.append({
                "title": "Gunakan Pendekatan Hati-hati",
                "description": "Analisis kuantitatif dan kualitatif berbeda. Gunakan pendekatan hati-hati dengan ukuran posisi kecil.",
                "priority": "sedang"
            })

        return recommendations


class BIEngine:
    """Main class yang menggabungkan semua fungsi"""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock_data = None
        self.news_data = None
        self.merged_data = None
        self.final_result = None

    def run(self) -> Dict[str, Any]:
        """
        Jalankan semua fungsi dan hasilkan output JSON untuk Next.js

        Returns:
            Dictionary yang siap untuk JSON response
        """
        try:
            logger.info(f"Memulai BI Engine untuk {self.ticker}")

            # Fungsi 1: Ambil data harga penutupan
            logger.info("Fungsi 1: Mengambil data harga penutupan...")
            self.stock_data = StockDataCollector.get_closing_prices(self.ticker)

            # Fungsi 2: Scrape berita
            logger.info("Fungsi 2: Scrape berita CNBC...")
            self.news_data = NewsScraper.get_world_markets_news()

            # Fungsi 3: Gabungkan data
            logger.info("Fungsi 3: Menggabungkan data...")
            self.merged_data = DataMerger.merge_data(self.stock_data, self.news_data)

            # Fungsi 4: Analisis performa pasar
            logger.info("Fungsi 4: Analisis performa pasar...")
            analysis = MarketAnalyzer.analyze_performance(self.merged_data)

            # Fungsi 5: Skor sentimen
            logger.info("Fungsi 5: Menghitung skor sentimen...")
            sentiment = SentimentScorer.calculate_sentiment_score(analysis)

            # Fungsi 6: Rekomendasi bisnis
            logger.info("Fungsi 6: Generate rekomendasi bisnis...")
            recommendations = BusinessRecommender.generate_recommendations(
                analysis,
                sentiment.get("score", 5)
            )

            # Format output untuk Next.js
            self.final_result = {
                "status": "success",
                "generated_at": datetime.now().isoformat(),
                "ticker": self.ticker,
                "data": {
                    # Data asli
                    "stock_data": self.stock_data,
                    "news_data": self.news_data,

                    # Hasil analisis
                    "analysis": analysis,

                    # Skor sentimen
                    "sentiment": sentiment,

                    # Rekomendasi
                    "recommendations": recommendations
                },
# Untuk frontend Next.js
                "json_ready": True
            }

            logger.info(f"BI Engine selesai untuk {self.ticker}")
            
# Simpan data ke Supabase jika environment variables tersedia
            self.save_to_supabase()
            
            return self.final_result

        except Exception as e:
            logger.error(f"Error fatal: {e}")
            return {
                "status": "error",
                "error": str(e),
                "ticker": self.ticker,
                "generated_at": datetime.now().isoformat()
}
    
    def save_to_supabase(self) -> Dict[str, Any]:
        """
        Simpan data analisis ke Supabase.
        Menggunakan strategi upsert untuk mencegah database bloat.
        
        Returns:
            Dictionary dengan status operasi
        """
        # Ambil credentials dari environment variables
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("SUPABASE_URL atau SUPABASE_KEY tidak ditemukan di environment variables")
            return {
                "success": False,
                "error": "SUPABASE_URL atau SUPABASE_KEY tidak ditemukan"
            }

        try:
            # ========== PROXY FIX: Remove proxy environment variables ==========
            # Supabase client doesn't support proxy argument, so we must unset these before creating client
            proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
            proxy_removed = []
            for key in proxy_vars:
                if key in os.environ:
                    proxy_removed.append(key)
                    del os.environ[key]
            
            # Log only if proxy vars were actually found and removed
            if proxy_removed:
                logger.info(f"Removed proxy env vars: {', '.join(proxy_removed)}")
            
            # Inisialisasi client Supabase dengan error handling
            try:
                supabase: Client = create_client(supabase_url, supabase_key)
            except TypeError as e:
                if "proxy" in str(e).lower():
                    logger.warning(f"Proxy error terdeteksi: {e}")
                    logger.warning("Melewati penyimpanan ke Supabase - main analysis tetap lanjut")
                    return {
                        "success": False,
                        "error": f"Proxy configuration error: {str(e)}"
                    }
                else:
                    raise
            
            logger.info(f"Menghubungkan ke Supabase: {supabase_url}")
            
            ticker = self.ticker
            generated_at = self.final_result.get("generated_at", datetime.now().isoformat())
            
            # ========== 1. Simpan ke stock_data ==========
            stock_data = self.final_result.get("data", {}).get("stock_data", {})
            if stock_data.get("success"):
                stock_record = stock_data.get("data", {})
                
                # Hapus data lama dengan ticker yang sama (strategi delete-before-insert)
                try:
                    supabase.table("stock_data").delete().eq("ticker", ticker).execute()
                except Exception as del_err:
                    logger.warning(f"Delete stock_data error (continuing): {del_err}")
                
                # Insert data baru
                try:
                    supabase.table("stock_data").insert({
                        "ticker": ticker,
                        "dates": stock_record.get("dates", []),
                        "closing_prices": stock_record.get("closing_prices", []),
                        "current_price": stock_record.get("current_price"),
                        "price_change": stock_record.get("price_change"),
                        "price_change_percent": stock_record.get("price_change_percent"),
                        "average_price": stock_record.get("average_price"),
                        "highest_price": stock_record.get("highest_price"),
                        "lowest_price": stock_record.get("lowest_price")
                    }).execute()
                    logger.info(f"Stock data disimpan untuk {ticker}")
                except Exception as ins_err:
                    logger.error(f"Insert stock_data error: {ins_err}")
            
            # ========== 2. Simpan ke news_data ==========
            news_data = self.final_result.get("data", {}).get("news_data", {})
            if news_data.get("success"):
                news_record = news_data.get("data", {})
                source = news_record.get("source", "CNBC World Markets")
                
                # Hapus data lama dengan source yang sama
                try:
                    supabase.table("news_data").delete().eq("source", source).execute()
                except Exception as del_err:
                    logger.warning(f"Delete news_data error (continuing): {del_err}")
                
                # Insert data baru
                try:
                    supabase.table("news_data").insert({
                        "source": source,
                        "headlines": news_record.get("headlines", []),
                        "total_found": news_record.get("total_found"),
                        "relevant_count": news_record.get("relevant_count")
                    }).execute()
                    logger.info(f"News data disimpan")
                except Exception as ins_err:
                    logger.error(f"Insert news_data error: {ins_err}")
            
            # ========== 3. Simpan ke merged_data ==========
            merged_data = self.merged_data
            if merged_data.get("success"):
                # Hapus data lama dengan ticker yang sama
                try:
                    supabase.table("merged_data").delete().eq("ticker", ticker).execute()
                except Exception as del_err:
                    logger.warning(f"Delete merged_data error (continuing): {del_err}")
                
                # Insert data baru
                try:
                    supabase.table("merged_data").insert({
                        "ticker": ticker,
                        "quantitative_data": merged_data.get("quantitative_data", {}),
                        "qualitative_data": merged_data.get("qualitative_data", {})
                    }).execute()
                    logger.info(f"Merged data disimpan untuk {ticker}")
                except Exception as ins_err:
                    logger.error(f"Insert merged_data error: {ins_err}")
            
            # ========== 4. Simpan ke sentiment_score ==========
            sentiment = self.final_result.get("data", {}).get("sentiment", {})
            if sentiment:
                score = sentiment.get("score", 5)
                label = sentiment.get("label", "netral").lower().replace(" ", "_")
                
                # Hapus data lama dengan score yang sama
                try:
                    supabase.table("sentiment_score").delete().eq("score", score).execute()
                except Exception as del_err:
                    logger.warning(f"Delete sentiment_score error (continuing): {del_err}")
                
                # Insert data baru
                try:
                    supabase.table("sentiment_score").insert({
                        "score": score,
                        "label": label,
                        "quantitative_score": sentiment.get("breakdown", {}).get("quantitative_score"),
                        "finbert_score": sentiment.get("breakdown", {}).get("finbert_score"),
                        "breakdown": sentiment.get("breakdown", {}),
                        "interpretation": sentiment.get("interpretation")
                    }).execute()
                    logger.info(f"Sentiment score disimpan: {score}/{label}")
                except Exception as ins_err:
                    logger.error(f"Insert sentiment_score error: {ins_err}")
            
            # ========== 5. Simpan ke recommendations ==========
            recommendations = self.final_result.get("data", {}).get("recommendations", [])
            if recommendations:
                # Hapus semua rekomendasi lama
                try:
                    supabase.table("recommendations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                except Exception:
                    # Alternative: truncate by deleting with a date filter or just continue
                    logger.warning("Delete all recommendations (trying alternative)...")
                    try:
                        supabase.table("recommendations").delete().is_("created_at", "not.null").execute()
                    except Exception:
                        pass  # Continue even if delete fails
                
                for rec in recommendations:
                    try:
                        supabase.table("recommendations").insert({
                            "title": rec.get("title"),
                            "description": rec.get("description"),
                            "priority": rec.get("priority", "rendah").lower()
                        }).execute()
                    except Exception as ins_err:
                        logger.error(f"Insert recommendation error: {ins_err}")
                logger.info(f"{len(recommendations)} rekomendasi disimpan")
            
            return {
                "success": True,
                "message": "Data berhasil disimpan ke Supabase",
                "ticker": ticker
            }
            
        except Exception as e:
            logger.error(f"Error menyimpan ke Supabase: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ==================== MAIN FUNCTION ====================
def run_bi_analysis(ticker: str) -> Dict[str, Any]:
    """
    Fungsi utama untuk menjalankan analisis BI

    Args:
        ticker: Simbol saham (contoh: 'AAPL', 'MSFT', 'GOOGL')

    Returns:
        Dictionary dengan output JSON siap untuk Next.js
    """
    engine = BIEngine(ticker)
    return engine.run()


def main():
    """Contoh penggunaan jika dijalankan langsung"""
    import sys

    # Default ticker jika tidak ada argumen
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

    print(f"\n{'='*60}")
    print(f"Business Intelligence Analysis")
    print(f"Ticker: {ticker}")
    print(f"{'='*60}\n")

    # Jalankan analisis
    result = run_bi_analysis(ticker)

    # Tampilkan hasil sebagai JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


if __name__ == "__main__":
    main()