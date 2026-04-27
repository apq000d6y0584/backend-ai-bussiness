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

import json
import re
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

import requests
import yfinance
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

        # Analisis kualitatif - berita
        headlines = news_data.get("headlines", [])

        # Hitung skor sentimen dari berita
        positive_count = 0
        negative_count = 0

        for headline in headlines:
            headline_lower = headline.lower()
            for kw in POSITIVE_KEYWORDS:
                if kw.lower() in headline_lower:
                    positive_count += 1
                    break
            for kw in NEGATIVE_KEYWORDS:
                if kw.lower() in headline_lower:
                    negative_count += 1
                    break

        total_analyzed = positive_count + negative_count
        if total_analyzed > 0:
            sentiment_ratio = positive_count / total_analyzed
        else:
            sentiment_ratio = 0.5  # Default netral

        if sentiment_ratio > 0.6:
            qualitative_trend = "positif"
        elif sentiment_ratio < 0.4:
            qualitative_trend = "negatif"
        else:
            qualitative_trend = "netral"

        # Ringkasan eksekutif
        ticker = merged_data.get("ticker", "N/A")
        executive_summary = (
            f"Analisis pasar untuk {ticker}: "
            f"Dari sisi kuantitatif, harga menunjukkan tren {quantitative_trend} "
            f"dengan perubahan {price_change:.2f}% dalam 7 hari terakhir. "
            f"Dari sisi kualitatif, sentiment berita menunjukkan kecenderungan {qualitative_trend} "
            f"({positive_count} berita positif, {negative_count} berita negatif). "
        )

        # Analisis sentimen gabungan
        combined_sentiment = (sentiment_ratio + (0.5 if price_change >= 0 else 0.5)) / 2

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
                "positive_news_count": positive_count,
                "negative_news_count": negative_count,
                "headlines_sample": headlines[:3]
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
        Hitung skor sentimen 1-10

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

        # Skor kualitatif (berdasarkan berita)
        positive = analysis_data.get("qualitative_analysis", {}).get("positive_news_count", 0)
        negative = analysis_data.get("qualitative_analysis", {}).get("negative_news_count", 0)

        total = positive + negative
        if total > 0:
            positive_ratio = positive / total
        else:
            positive_ratio = 0.5

        # Mapping ratio ke skor 1-10
        if positive_ratio >= 0.9:
            k_score = 10
        elif positive_ratio >= 0.7:
            k_score = 8
        elif positive_ratio >= 0.6:
            k_score = 7
        elif positive_ratio >= 0.4:
            k_score = 5
        elif positive_ratio >= 0.3:
            k_score = 3
        elif positive_ratio >= 0.1:
            k_score = 2
        else:
            k_score = 1

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

        return {
            "score": final_score,
            "label": label,
            "breakdown": {
                "quantitative_score": q_score,
                "quantitative_weight": "40%",
                "qualitative_score": k_score,
                "qualitative_weight": "60%"
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
            return self.final_result

        except Exception as e:
            logger.error(f"Error fatal: {e}")
            return {
                "status": "error",
                "error": str(e),
                "ticker": self.ticker,
                "generated_at": datetime.now().isoformat()
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