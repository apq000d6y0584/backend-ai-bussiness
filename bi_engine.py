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
_proxy_vars = [
    'HTTP_PROXY', 'HTTPS_PROXY',
    'http_proxy', 'https_proxy',
    'ALL_PROXY', 'all_proxy',
    'NO_PROXY', 'no_proxy'
]
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
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path

import requests
import yfinance
from bs4 import BeautifulSoup
import numpy as np

# ========== PROXY FIX: Import supabase with error handling ========== 
try:
    from supabase import create_client, Client
except TypeError as _e:
    if "proxy" in str(_e).lower():
        import sys
        _mods_to_remove = [k for k in sys.modules if 'supabase' in k or 'http' in k]
        for _m in _mods_to_remove:
            sys.modules.pop(_m, None)
        from supabase import create_client, Client
    else:
        raise
# ========== End supabase import fix ========== 

from transformers import pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DLAnalyzer:
    """Deep Learning Analyzer menggunakan FinBERT (pipeline)."""

    _instance = None
    _sentiment_pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DLAnalyzer, cls).__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._sentiment_pipeline is None:
            model_name = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
            logger.info(f"Menginisialisasi model ringan: {model_name}...")
            self._sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                device=-1
            )
            logger.info("DistilRoBERTa berhasil dimuat!")

    def analyze_sentiment(self, headlines: List[str]) -> Dict[str, Any]:
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

        results: List[Dict[str, Any]] = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for headline in headlines:
            try:
                text = headline[:512] if len(headline) > 512 else headline
                output = self._sentiment_pipeline(text)[0]
                label = output['label'].lower()
                score = output['score']

                if label == 'positive':
                    mapped_score = round(5 + (score * 5))
                    mapped_score = min(10, max(6, mapped_score))
                    positive_count += 1
                elif label == 'negative':
                    mapped_score = round(5 - (score * 5))
                    mapped_score = min(5, max(1, mapped_score))
                    negative_count += 1
                else:
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

        total = len(results)
        avg_score = sum(r['mapped_score'] for r in results) / total if total else 5.0
        avg_score = round(avg_score, 1)

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


CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_DURATION = 3600

BUSINESS_KEYWORDS = [
    "stock", "market", "trade", "economy", "economic", "finance",
    "investment", "investor", "share", "shares", "dividend", "profit",
    "revenue", "earnings", "growth", "quarter", "fiscal", "CEO",
    "company", "business", "merger", "acquisition", "bull", "bear",
    "index", "nasdaq", "dow", "spy", "federal", "reserve", "inflation",
    "interest", "rate", "gdp", "consumer", "price", "outlook", "forecast"
]


class VolatilityCalculator:
    @staticmethod
    def calc_volatility(closing_prices: List[float]) -> Dict[str, Any]:
        if not isinstance(closing_prices, list) or len(closing_prices) < 3:
            return {"volatility": 0.0, "volatility_percent": 0.0, "returns": [], "n_returns": 0}

        prices = [p for p in closing_prices if isinstance(p, (int, float)) and p > 0]
        if len(prices) < 3:
            return {"volatility": 0.0, "volatility_percent": 0.0, "returns": [], "n_returns": 0}

        returns = []
        for i in range(1, len(prices)):
            prev = prices[i - 1]
            cur = prices[i]
            if prev <= 0:
                continue
            returns.append((cur - prev) / prev)

        if not returns:
            return {"volatility": 0.0, "volatility_percent": 0.0, "returns": [], "n_returns": 0}

        vol = float(np.std(returns, ddof=0))
        return {
            "volatility": vol,
            "volatility_percent": round(vol * 100.0, 4),
            "returns": returns[-10:],
            "n_returns": len(returns)
        }


class CacheManager:
    @staticmethod
    def _get_cache_key(prefix: str, ticker: str = "") -> str:
        raw = f"{prefix}:{ticker}:{datetime.now().date()}"
        return hashlib.md5(raw.encode()).hexdigest()

    @staticmethod
    def get(prefix: str, ticker: str = "") -> Optional[Dict]:
        cache_file = CACHE_DIR / f"{CacheManager._get_cache_key(prefix, ticker)}.json"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            cache_time = cached.get("timestamp", 0)
            if time.time() - cache_time > CACHE_DURATION:
                cache_file.unlink(missing_ok=True)
                return None
            logger.info(f"Cache hit: {prefix} - {ticker}")
            return cached.get("data")
        except Exception as e:
            logger.warning(f"Cache error: {e}")
            return None

    @staticmethod
    def set(prefix: str, ticker: str, data: Dict) -> None:
        cache_file = CACHE_DIR / f"{CacheManager._get_cache_key(prefix, ticker)}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({"timestamp": time.time(), "data": data}, f, indent=2, ensure_ascii=False)
            logger.info(f"Cache saved: {prefix} - {ticker}")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


class StockDataCollector:
    @staticmethod
    def get_closing_prices(ticker: str, days: int = 7) -> Dict[str, Any]:
        cache_key = f"stock_{ticker}_{days}"
        _ = cache_key  # kept for compatibility

        cached_data = CacheManager.get("stock", ticker)
        if cached_data:
            return cached_data

        try:
            stock = yfinance.Ticker(ticker)
            hist = stock.history(period=f"{days + 5}d", interval="1d")

            if hist.empty:
                return {"success": False, "error": f"Tidak ada data untuk ticker {ticker}", "ticker": ticker}

            closing_prices: List[float] = []
            dates: List[str] = []
            for idx, row in hist.iterrows():
                if len(closing_prices) >= days:
                    break
                if row['Close'] > 0:
                    closing_prices.append(round(float(row['Close']), 2))
                    dates.append(idx.strftime("%Y-%m-%d"))

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

            CacheManager.set("stock", ticker, result)
            return result

        except Exception as e:
            return {"success": False, "error": f"Yahoo/connection error: {str(e)}", "ticker": ticker}


class NewsScraper:
    """Scrape judul berita dari CNBC World Markets dengan retry + fallback cache."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*
