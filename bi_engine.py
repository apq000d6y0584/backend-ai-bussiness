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
# Supabase is optional for this module; import failures should not prevent API startup.
try:
    from supabase import create_client, Client  # type: ignore
except ModuleNotFoundError:
    create_client = None  # type: ignore
    Client = None  # type: ignore
except TypeError as _e:
    if "proxy" in str(_e).lower():
        import sys
        _mods_to_remove = [k for k in sys.modules if 'supabase' in k or 'http' in k]
        for _m in _mods_to_remove:
            sys.modules.pop(_m, None)
        from supabase import create_client, Client  # type: ignore
    else:
        raise
# ========== End supabase import fix ========== 

# transformers is heavy/optional; allow API startup without it.
try:
    from transformers import pipeline  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    pipeline = None  # type: ignore

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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*",
    }

    @staticmethod
    def get_world_markets_news() -> Dict[str, Any]:
        """Return a lightweight news payload.

        Note: If scraping fails, return cached/empty fallback instead of raising.
        """
        cache_key = "news_world_markets"
        cached = CacheManager.get("news", cache_key)
        if cached:
            return {"success": True, "source": "cnbc", "data": cached, "fallback_strategy": "cache"}

        url = "https://www.cnbc.com/world/?region=world"
        try:
            resp = requests.get(url, headers=NewsScraper.HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Heuristic: collect headline-like elements
            headlines: List[str] = []
            for tag in soup.find_all(['h1', 'h2', 'h3']):
                txt = tag.get_text(strip=True)
                if not txt:
                    continue
                if any(k.lower() in txt.lower() for k in BUSINESS_KEYWORDS) or len(txt) >= 20:
                    headlines.append(txt)
                if len(headlines) >= 20:
                    break

            payload = {
                "headlines": headlines,
                "count": len(headlines),
            }
            CacheManager.set("news", cache_key, payload)
            return {"success": True, "source": "cnbc", "data": payload, "fallback_strategy": None}
        except Exception as e:
            # Fallback: empty but successful so API can still respond
            logger.warning(f"News scrape failed: {e}")
            return {
                "success": False,
                "source": "cnbc",
                "data": {"headlines": [], "count": 0},
                "error": str(e),
                "fallback_strategy": "empty"
            }


class IHSGDashboardEngine:
    """Price-only heuristic IHSG dashboard engine.

    Karena opsi yang dipilih adalah nomor (1): hanya berbasis harga (yfinance).
    Kategori growth/value/bullish/bearish/multibagger/bagholder/value_trap/zombie dibuat sebagai proxy berbasis
    momentum, drawdown, volatilitas, dan return beberapa horizon.
    """

    # Hardcoded small universe (±20 likuid) menggunakan format yfinance '.JK'
    # Note: Jika yfinance tidak menemukan ticker tertentu, engine akan skip.
    IHSG_UNIVERSE_JK = [
        "BBCA.JK", "BMRI.JK", "BBRI.JK", "TLKM.JK", "ASII.JK", "UNTR.JK", "MDKA.JK", "ANTM.JK",
        "KLBF.JK", "BBTN.JK", "ADRO.JK", "PTBA.JK", "BRPT.JK", "SMGR.JK", "TLKM.JK",
        "INCO.JK", "CTRA.JK", "GOTO.JK", "KLBF.JK", "AKRA.JK"
    ]

    @staticmethod
    def _safe_float(x: Any, default: float = 0.0) -> float:
        try:
            if x is None:
                return default
            return float(x)
        except Exception:
            return default

    @staticmethod
    def _calc_return_pct(closing_prices: List[float]) -> float:
        if not isinstance(closing_prices, list) or len(closing_prices) < 2:
            return 0.0
        start = closing_prices[0]
        end = closing_prices[-1]
        if start == 0:
            return 0.0
        return ((end - start) / start) * 100.0

    @classmethod
    def _get_universe_data(cls, ticker: str, window_days: int, price_horizon_days: int) -> Optional[Dict[str, Any]]:
        # window_prices: untuk ranking (window_days)
        # horizon_prices: untuk multibagger/bagholder proxy (price_horizon_days)
        # yfinance collector hanya ambil 'days' closing prices, jadi kita panggil beberapa kali.
        win = StockDataCollector.get_closing_prices(ticker, days=window_days)
        hor = StockDataCollector.get_closing_prices(ticker, days=price_horizon_days)

        if not win.get("success") or not hor.get("success"):
            return None

        win_prices = (win.get("data") or {}).get("closing_prices") or []
        hor_prices = (hor.get("data") or {}).get("closing_prices") or []

        window_return = cls._calc_return_pct(win_prices)
        horizon_return = cls._calc_return_pct(hor_prices)

        vol_window = VolatilityCalculator.calc_volatility(win_prices)
        vol_horizon = VolatilityCalculator.calc_volatility(hor_prices)

        # Drawdown proxy: (max - last) / max dalam window horizon.
        max_price = max(hor_prices) if hor_prices else 0.0
        last_price = hor_prices[-1] if hor_prices else 0.0
        drawdown_pct = ((max_price - last_price) / max_price) * 100.0 if max_price else 0.0

        # Momentum rank helpers
        momentum_score = window_return  # langsung; proxy paling sederhana

        return {
            "ticker": ticker,
            "window_return_pct": round(window_return, 4),
            "horizon_return_pct": round(horizon_return, 4),
            "drawdown_pct": round(drawdown_pct, 4),
            "volatility_window": float(vol_window.get("volatility_percent", 0.0)),
            "volatility_horizon": float(vol_horizon.get("volatility_percent", 0.0)),
        }

    @classmethod
    def _rank_top_bottom(cls, universe_rows: List[Dict[str, Any]], key: str, top_n: int) -> List[Dict[str, Any]]:
        rows = [r for r in universe_rows if isinstance(r.get(key), (int, float))]
        rows_sorted = sorted(rows, key=lambda x: x.get(key, 0.0))
        bottom = rows_sorted[:top_n]
        top = rows_sorted[-top_n:][::-1]
        return {"top": top, "bottom": bottom}

    @classmethod
    def _score_item(cls, row: Dict[str, Any], primary: float, secondary: float = 0.0) -> float:
        # Skor 0-100-ish; clamp
        raw = primary * 1.0 + secondary * 0.2
        return float(max(0.0, min(100.0, raw)))

    @classmethod
    def run(cls, window_days: int = 30, top_n: int = 5, price_horizon_days: int = 200) -> Dict[str, Any]:
        generated_at = datetime.now().isoformat()

        rows: List[Dict[str, Any]] = []
        for t in cls.IHSG_UNIVERSE_JK:
            data = cls._get_universe_data(t, window_days=window_days, price_horizon_days=price_horizon_days)
            if data:
                rows.append(data)

        if not rows:
            return {
                "status": "success",
                "generated_at": generated_at,
                "window_days": window_days,
                "price_horizon_days": price_horizon_days,
                "universe_used": 0,
                "categories": {
                    "top_gainers": [],
                    "top_losers": [],
                    "growth_stocks": [],
                    "value_stocks": [],
                    "bullish_stocks": [],
                    "bearish_stocks": [],
                    "multibagger_stocks": [],
                    "bagholder_stocks": [],
                    "value_trap_stocks": [],
                    "zombie_stocks": [],
                }
            }

        key_return_window = "window_return_pct"
        key_return_horizon = "horizon_return_pct"

        ranked = cls._rank_top_bottom(rows, key_return_window, top_n=top_n)
        top_gainers_rows = ranked["top"]
        top_losers_rows = ranked["bottom"]

        # growth vs value proxy:
        # - growth: momentum tinggi + volatilitas cukup (aktif)
        # - value: momentum rendah + volatilitas rendah (proxy “lebih stabil/murah relatif”) 
        growth_candidates = sorted(
            rows,
            key=lambda r: (r.get("window_return_pct", 0.0) - (r.get("volatility_window", 0.0) * 0.02))
        )
        growth_candidates = growth_candidates[-top_n:][::-1]

        value_candidates = sorted(
            rows,
            key=lambda r: (r.get("window_return_pct", 0.0) + (r.get("volatility_window", 0.0) * 0.01))
        )
        value_candidates = value_candidates[:top_n]

        # bullish vs bearish proxy based on window return + volatility (risk-adjusted)
        bullish_sorted = sorted(rows, key=lambda r: r.get("window_return_pct", 0.0) - r.get("volatility_window", 0.0) * 0.01)
        bullish_rows = bullish_sorted[-top_n:][::-1]

        bearish_sorted = sorted(rows, key=lambda r: r.get("window_return_pct", 0.0) - r.get("volatility_window", 0.0) * 0.01)
        bearish_rows = bearish_sorted[:top_n]

        # multibagger vs bagholder proxy based on horizon return and drawdown
        multibagger_sorted = sorted(
            rows,
            key=lambda r: r.get("horizon_return_pct", 0.0) - (r.get("drawdown_pct", 0.0) * 0.05)
        )
        multibagger_rows = multibagger_sorted[-top_n:][::-1]

        bagholder_sorted = sorted(
            rows,
            key=lambda r: r.get("horizon_return_pct", 0.0) - (r.get("drawdown_pct", 0.0) * 0.05)
        )
        bagholder_rows = bagholder_sorted[:top_n]

        # value trap proxy: “value-like” (low momentum) but horizon return negatif
        value_like = sorted(rows, key=lambda r: r.get("window_return_pct", 0.0))[: max(top_n * 2, top_n)]
        value_trap_scored = sorted(
            value_like,
            key=lambda r: r.get("horizon_return_pct", 0.0)  # paling negatif dulu
        )
        value_trap_rows = value_trap_scored[:top_n]

        # zombie proxy: low momentum + low volatility + horizon return mendekati nol/negatif
        zombie_sorted = sorted(
            rows,
            key=lambda r: (abs(r.get("window_return_pct", 0.0)) * 0.2) + (r.get("volatility_window", 0.0) * 0.05) - r.get("horizon_return_pct", 0.0)
        )
        # Ambil kandidat dengan “paling zombie”: abs momentum kecil, volatility rendah, horizon return jelek
        zombie_rows = zombie_sorted[:top_n]

        def to_out_list(item_rows: List[Dict[str, Any]]):
            out = []
            for r in item_rows:
                ret = float(r.get("window_return_pct", 0.0))
                score = cls._score_item(r, primary=ret, secondary=-r.get("drawdown_pct", 0.0))
                out.append({
                    "ticker": r.get("ticker"),
                    "return_pct": round(ret, 4),
                    "volatility_percent": round(float(r.get("volatility_window", 0.0)), 4),
                    "drawdown_pct": round(float(r.get("drawdown_pct", 0.0)), 4),
                    "score": round(float(score), 2),
                })
            return out

        # For categories that rely on horizon return, map return_pct to horizon for better semantics.
        def to_out_list_horizon(item_rows: List[Dict[str, Any]]):
            out = []
            for r in item_rows:
                ret = float(r.get("horizon_return_pct", 0.0))
                score = cls._score_item(r, primary=ret, secondary=-r.get("drawdown_pct", 0.0))
                out.append({
                    "ticker": r.get("ticker"),
                    "return_pct": round(ret, 4),
                    "volatility_percent": round(float(r.get("volatility_horizon", 0.0)), 4),
                    "drawdown_pct": round(float(r.get("drawdown_pct", 0.0)), 4),
                    "score": round(float(score), 2),
                })
            return out

        return {
            "status": "success",
            "generated_at": generated_at,
            "window_days": window_days,
            "price_horizon_days": price_horizon_days,
            "universe_used": len(rows),
            "categories": {
                "top_gainers": to_out_list(top_gainers_rows),
                "top_losers": to_out_list(top_losers_rows),
                "growth_stocks": to_out_list(growth_candidates),
                "value_stocks": to_out_list(value_candidates),
                "bullish_stocks": to_out_list(bullish_rows),
                "bearish_stocks": to_out_list(bearish_rows),
                "multibagger_stocks": to_out_list_horizon(multibagger_rows),
                "bagholder_stocks": to_out_list_horizon(bagholder_rows),
                "value_trap_stocks": to_out_list(value_trap_rows),
                "zombie_stocks": to_out_list(zombie_rows),
            }
        }


class BIEngine:
    """Orchestrates stock data + news + sentiment + recommendations."""

    def __init__(self, ticker: str):
        self.ticker = ticker
        self._sentiment_analyzer = DLAnalyzer()


    def run(
        self,
        detail: str = "summary",
        days: int = 7,
        headline_limit: int = 10,
        finbert_positive_threshold: float = 7.0,
        finbert_negative_threshold: float = 4.0,
        sentiment_positive_threshold: float = 7.0,
        sentiment_negative_threshold: float = 3.0,
    ) -> Dict[str, Any]:
        generated_at = datetime.now().isoformat()

        # Stock data
        stock_result = StockDataCollector.get_closing_prices(self.ticker, days)
        if not stock_result.get("success"):
            return {
                "status": "error",
                "ticker": self.ticker,
                "generated_at": generated_at,
                "error": stock_result.get("error", "failed to fetch stock data"),
                "data": None,
            }

        # News data
        news_result = NewsScraper.get_world_markets_news()
        headlines = (news_result.get("data") or {}).get("headlines") or []
        headlines = [h for h in headlines if isinstance(h, str)][: int(headline_limit) or 10]

        # Sentiment
        sentiment = self._sentiment_analyzer.get_average_sentiment(headlines)
        finbert_score = float(sentiment.get("score", 5.0))

        # Quantitative analysis (simple heuristic)
        closing_prices = (stock_result.get("data") or {}).get("closing_prices") or []
        vol = VolatilityCalculator.calc_volatility(closing_prices)
        price_change = float((stock_result.get("data") or {}).get("price_change_percent") or 0.0)

        quantitative_analysis = {
            "price_change_percent": price_change,
            "volatility": vol.get("volatility", 0.0),
            "volatility_percent": vol.get("volatility_percent", 0.0),
        }

        # Recommendations
        # Use thresholds to create a deterministic output
        if finbert_score >= finbert_positive_threshold and price_change >= 0:
            recs = [
                {"strategy": "Buy (positive momentum)", "confidence": round(min(0.99, 0.5 + finbert_score / 20), 2)},
                {"strategy": "Hold / Accumulate on dips", "confidence": 0.62},
                {"strategy": "Risk-managed entry", "confidence": 0.55},
            ]
            overall = "Bullish"
        elif finbert_score <= finbert_negative_threshold or price_change < 0:
            recs = [
                {"strategy": "Avoid / Reduce exposure", "confidence": round(min(0.99, 0.5 + (10 - finbert_score) / 20), 2)},
                {"strategy": "Wait for confirmation", "confidence": 0.65},
                {"strategy": "Hedge with protective puts", "confidence": 0.58},
            ]
            overall = "Bearish"
        else:
            recs = [
                {"strategy": "Neutral: Hold with monitoring", "confidence": 0.6},
                {"strategy": "Scale in gradually", "confidence": 0.55},
                {"strategy": "Focus on catalysts", "confidence": 0.52},
            ]
            overall = "Neutral"

        # Sentiment + threshold mapping (server expects these names in some places)
        if sentiment.get("label") and isinstance(sentiment["label"], str):
            sentiment_label = sentiment["label"]
        else:
            sentiment_label = "Netral"

        if sentiment_label.lower() in {"positif", "positive"}:
            sentiment_category = "positive"
        elif sentiment_label.lower() in {"negatif", "negative"}:
            sentiment_category = "negative"
        else:
            sentiment_category = "neutral"

        sentiment_payload = {
            "score": finbert_score,
            "label": sentiment_label,
            "category": sentiment_category,
            "breakdown": sentiment.get("breakdown", {}),
        }

        analysis_payload = {
            "quantitative_analysis": quantitative_analysis,
            "volatility_analysis": vol,
            "overall": overall,
        }

        # Build response based on detail
        data: Dict[str, Any] = {
            "stock_data": stock_result.get("data"),
            "news_data": news_result.get("data"),
            "sentiment": sentiment_payload,
            "recommendations": recs,
            "analysis": analysis_payload,
        }

        if detail == "summary":
            # remove long news headlines list if present
            if isinstance(data.get("news_data"), dict):
                data["news_data"] = {
                    "count": data["news_data"].get("count", 0),
                }

        return {
            "status": "success",
            "ticker": self.ticker,
            "generated_at": generated_at,
            "data": data,
        }



